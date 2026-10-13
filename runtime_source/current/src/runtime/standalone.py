"""Continuous line owner: existing vision + frozen assembly, then one PLC result.

Software acquisition starts without a browser. Physical Run remains PLC-owned.
The upstream sensor opens a serial arrival window; only its first unambiguous
new track can be bound. No previous-product pose or prediction is inherited.
"""
import json
import queue
import threading
import time
import uuid
from datetime import datetime, timezone

from src.control.standalone_plc import LineHandshake
from src.runtime.production import ProductionRuntime
from src.runtime.inspection_bridge import InspectionBridge
from src.runtime.production_profile import calibration_sha
from src.vision.integrated_decision import combine_decisions


def arrival_evidence(packet, accepted_at, epoch, generation, zone):
    """Geometry/freshness only; class labels are not arguments."""
    if not packet or packet['monotonic_s'] <= accepted_at:
        return False
    if packet['camera_epoch'] != epoch or packet['generation'] != generation:
        return False
    observations = packet.get('provider', {}).get('observations', [])
    if len(observations) != 1 or not packet['integrity']['valid']:
        return False
    box = observations[0]['bbox']
    x1, y1 = zone['polygon_normalized'][0]
    x2, y2 = zone['polygon_normalized'][2]
    return bool(x1 < box['x1'] < box['x2'] < x2 and y1 < box['y1'] < box['y2'] < y2)


class StandaloneRuntime(ProductionRuntime):
    OBSERVATION_ISSUES = frozenset({
        'TRACK_ASSOCIATION_OR_GAP_LOST', 'PRODUCT_OBSERVATION_GAP',
        'INVALID_OR_STALE_PRODUCT_OBSERVATION', 'PRODUCT_FRAME_ORDER_INVALID',
        'MULTIPLE_PRODUCT_AMBIGUITY', 'PRODUCT_DEPARTURE_NOT_OBSERVED',
    })

    def __init__(self, *args, line_profile, assembly, **kwargs):
        self.configured = threading.Event()
        self.line_profile, self.assembly = dict(line_profile), assembly
        self.arrival = None
        self.assembly_submitted = {}
        self.recovery_at = 0
        self.camera_retry_at = 0
        self.camera_recovery = None
        self.issue = None
        self.cycle_issue = None
        self.line_wait = 'INITIALIZING'
        super().__init__(*args, **kwargs)
        self.shadow = assembly  # Reuse existing evidence routes, not post-commit shadow dispatch.
        self.service.journal.outbox_limit = None  # Optional notebook export is not a PLC dependency.
        self.service.journal.min_free_bytes = line_profile['min_free_bytes']
        self.configured.set()

    def start_auto(self):
        raise ValueError('PHYSICAL_START_OWNS_LINE_RUN; SOFTWARE_ACQUISITION_IS_AUTOMATIC')

    def _fault(self, reason):
        if (getattr(self.gateway, 'contract_version', None) == 'LEGACY_THREE_BOOL'
                and reason in self.OBSERVATION_ISSUES and self.operating and not self.error):
            self._observation_issue(reason)
            return
        super()._fault(reason)
        if self.handshake.state != 'RESYNC_REQUIRED':
            self.handshake.fault(reason, 'BLOCKED')

    def _observation_issue(self, reason):
        """Keep acquisition alive; never recycle an accepted product's identity."""
        if self.cycle_issue:
            return
        now = time.monotonic()
        unbound = (self.handshake.token is None and self.handshake.state in ('SYNC_LOW', 'ARMED')
                   and not self.service.active and not self.bridge.inspection_id)
        self.issue = dict(reason=reason, scope='UNBOUND_PREVIEW' if unbound else 'REQUEST',
            request_token=self.handshake.token, inspection_id=self.bridge.inspection_id,
            occurred_at=datetime.now(timezone.utc).isoformat(), monotonic_s=now,
            active=not unbound, action='REACQUIRE_PREVIEW' if unbound else 'WAIT_VERIFIED_PRODUCT_CLEAR')
        self._event(dict(event='LINE_OBSERVATION_ISSUE', **self.issue))
        self.eligible = False
        if unbound:
            self._reset_unbound_observation(now)
            return
        self.cycle_issue = dict(self.issue)
        # Preserve the raw worker record. A late PASS can only become ERROR for
        # this token; it cannot enter the next request or be sent to the PLC.
        if self.service.active:
            self.service.cancel(self.service.active['inspection_id'])
        elif self.handshake.state == 'REQUEST_LATCHED':
            self._finish_without_frames('ERROR', reason, now)

    def _reset_unbound_observation(self, now):
        self._replace_tracking_session(uuid.uuid4().hex)
        self.inspected_tracks.clear()
        self.window_event = None
        self.eligible = False
        self.new_product_after = now
        self._reset_departure_candidate()
        self.area_window.reset()

    def _observation_hold(self, packet, provider):
        issue = self.cycle_issue
        if not issue:
            return False
        # Parent validated packet identity, age, absence and the configured area
        # evidence already. Request OFF or a timeout is never product clearance.
        area = self.area_observation or {}
        healthy_clear = bool(self.area_config_version and self._absence_ready()
            and self._area_approval_current(area) and area.get('state') == 'CLEAR'
            and area.get('first_clear_monotonic', -1) >= issue['monotonic_s']
            and not self.service.active and not self.service.error)
        self._diagnostic_reason = 'REQUEST_ISSUE_OBSERVING_FOR_CLEARANCE'
        if (healthy_clear and self.handshake.state == 'WAIT_PRODUCT_CLEAR'
                and self.handshake.release_cleared_cycle(product_clear=True)):
            self._event(dict(event='LINE_REQUEST_ISSUE_CLEARED', previous_issue=issue,
                             clearance_frame_id=packet['frame_id'], plc_writes=0))
            self._reset_unbound_observation(time.monotonic())
            self.arrival = None
            self.cycle_issue = None
            self.issue = dict(issue, active=False, action='CLEARED_WAIT_NEW_REQUEST')
        return True

    def stop_auto(self):
        # Maintenance stop cannot assert motion. Physical independent STOP remains required.
        with self.lock, self.service.lock:
            self._fault('LOCAL_MAINTENANCE_HOLD')
            self.handshake.fault('LOCAL_MAINTENANCE_HOLD', 'BLOCKED')
            self.handshake.shutdown()
            return self.status()

    def _profile_ready(self):
        return bool(self.line_profile.get('field_profile_verified') is True
            and self.zone.get('confirmed')
            and self.zone.get('calibration_sha') == calibration_sha(self.service.calibration)
            and self.area_config_version)

    def _clear(self, now):
        area = self.area_observation
        return bool(self._absence_ready() and self._area_approval_current(area)
            and area['state'] == 'CLEAR' and self.coordinator.active_cycle is None
            and not self.service.active and self.latest_packet
            and 0 <= now-self.latest_packet['processed_monotonic'] < 2)

    def _area_transaction_block(self):
        if (getattr(self.gateway, 'contract_version', None) != 'LEGACY_THREE_BOOL'
                or self.handshake.state != 'WAIT_PRODUCT_CLEAR'):
            return super()._area_transaction_block()
        # A withdrawn request may retire visually without a PLC publication.
        # The cancelled worker must finish first; no fabricated ACK or CLEAR.
        if not self.operating or self.error:
            return 'USER_STOP_OR_SYSTEM_FAULT'
        if (getattr(self.service, 'error', None) or
                getattr(self.service, 'state', 'IDLE') in ('RECOVERY', 'STOPPED', 'CANCELLING')):
            return 'INSPECTION_SERVICE_OR_CAMERA_FAULT'
        if self.service.active:
            return 'INSPECTION_IN_FLIGHT'
        if self.bridge.inspection_id and self.bridge.inspection_id not in self.published_ids:
            return 'RESULT_NOT_SETTLED'
        if self.handshake.reason not in ('LEGACY_REQUEST_WITHDRAWN_RESULT_BLOCKED',
                                        'LEGACY_COMPLETED_WAIT_PRODUCT_CLEAR',
                                        'LEGACY_BOOL_UNREPRESENTABLE_REVIEW',
                                        'LEGACY_BOOL_UNREPRESENTABLE_ERROR'):
            return 'LEGACY_TRANSACTION_UNSETTLED'
        return None

    def _cancel_pending(self, reason):
        if self.bridge.inspection_id and self.bridge.inspection_id not in self.published_ids:
            self.published_ids.add(self.bridge.inspection_id)
            self._event(dict(event='LINE_CANCELLED_RESULT_BLOCKED', inspection_id=self.bridge.inspection_id, reason=reason))
        if self.service.active:
            self.service.cancel(self.service.active['inspection_id'])
        self.arrival = None

    def _poll_plc(self, now):
        if now < self.next_plc_poll_at: return
        self.next_plc_poll_at = now + .1
        if getattr(self.gateway, 'contract_version', None) == 'LEGACY_THREE_BOOL':
            self._poll_legacy_plc(now)
            return
        if self.handshake.state == 'RESYNC_REQUIRED':
            self._cancel_pending(self.handshake.reason)
            self.line_wait = self.handshake.reason
            if now < self.recovery_at or self.service.active: return
            self.recovery_at = now + 5
            # New session is the only reconnect path. Never retry an uncertain result.
            # PLC V3 drops Run on session change and requires a fresh physical Start.
            previous = self.handshake.status()
            self.gateway.close()
            session = self.service.journal.new_session('standalone-line')
            self.handshake = LineHandshake(self.gateway, self._event, session_id=session)
            self._event(dict(event='LINE_RESYNC_NEW_SESSION', previous=previous, new_session=session))
            self._replace_tracking_session(uuid.uuid4().hex)
            self.bridge = InspectionBridge(self.service, self.coordinator)
            self.inspected_tracks.clear()
            self.absent.clear()
            self.error = None
            self.latest_packet = None
            self.epoch = None
            self.last_sequence, self.last_time = -1, 0
            self.worker_generation = self.service.generation
            self.eligible = False
            self.observation_started_at = now
            self._reset_departure_candidate()
        previous = self.handshake.token
        clear = self._clear(now)
        ready = bool(self.operating and not self.error and self._profile_ready()
            and self.assembly.ready and self.service.status()['ready'])
        self.handshake.service_tick(now, ready=ready, product_clear=clear)
        if self.handshake.state == 'RESYNC_REQUIRED':
            self._cancel_pending(self.handshake.reason)
            self.operating = False
            return
        if self.handshake.token and self.handshake.token != previous:
            # A pre-existing track at the sensor edge cannot silently be adopted.
            track = self.coordinator._tracker._track_id
            self.arrival = dict(token=self.handshake.token, epoch=self.epoch,
                generation=self.service.generation, track=None, conveyor_off_at=None,
                preexisting_track=track)
            self._event(dict(event='UPSTREAM_ENTRY_ACCEPTED', line_cycle_id=self.handshake.cycle_id,
                             camera_epoch=self.epoch, preexisting_track=track))
        self.line_wait = (self.handshake.reason or ('WAIT_FIELD_PROFILE' if not self._profile_ready()
            else 'WAIT_ASSEMBLY_MODEL' if not self.assembly.ready
            else 'READY_WAIT_PHYSICAL_START' if not self.handshake.inputs.get('PLC_RunPermit')
            else self.handshake.state))

    def _poll_legacy_plc(self, now):
        """Existing three-tag ladder: software readiness is not PLC Run permission."""
        previous = self.handshake.token
        self.handshake.poll(now)
        if self.handshake.state == 'RESYNC_REQUIRED':
            self._cancel_pending(self.handshake.reason)
            self.line_wait = self.handshake.reason
            if not self.error:
                self._fault(self.handshake.reason)
            return
        if self.handshake.state == 'WAIT_PRODUCT_CLEAR':
            if self.handshake.early_off:
                self._cancel_pending(self.handshake.reason)
            after = self.handshake.clearance_required_after
            area = self.area_observation or {}
            fresh_clear = bool(self._clear(now) and self.latest_packet
                and self.latest_packet['monotonic_s'] > after
                and area.get('first_clear_monotonic', -1) >= after)
            if not self.handshake.release_cleared_cycle(product_clear=fresh_clear):
                self.line_wait = self.handshake.reason
                return
            self.arrival = None
        if self.handshake.token and self.handshake.token != previous:
            track = self.coordinator._tracker._track_id
            self.arrival = dict(token=self.handshake.token, epoch=self.epoch,
                generation=self.service.generation, track=None, preexisting_track=track)
            self._event(dict(event='LEGACY_UPSTREAM_REQUEST_ACCEPTED',
                camera_epoch=self.epoch, preexisting_track=track,
                plc_cycle_id=None, sensor_or_stop_off_distinguishable=False))
        self.line_wait = (self.handshake.reason or
            ('WAIT_FIELD_PROFILE' if not self._profile_ready() else
             'WAIT_ASSEMBLY_MODEL' if not self.assembly.ready else
             'LEGACY_READ_ONLY_STANDBY' if not getattr(self.gateway, 'writes_enabled', False) else
             'READY_WAIT_EXISTING_PLC_REQUEST' if self.handshake.state == 'ARMED' else
             self.handshake.state))

    def _trigger(self, now):
        if self.handshake.state != 'REQUEST_LATCHED' or self.service.active: return
        if getattr(self.gateway, 'contract_version', None) == 'LEGACY_THREE_BOOL':
            self._trigger_legacy(now)
            return
        elapsed = now - self.handshake.accepted_at
        expired = elapsed >= self.line_profile['arrival_deadline_s']
        if expired:
            self._finish_without_frames('ERROR', 'NO_INSPECTION_ARRIVAL_OR_STOP_NOT_CONFIRMED', now)
            return
        context = self.arrival
        if not context or context['preexisting_track'] is not None: return
        if self.error or not self.operating: return
        packet = self.latest_packet
        if not arrival_evidence(packet, self.handshake.accepted_at, context['epoch'],
                                context['generation'], self.zone): return
        track = self.coordinator._tracker._track_id
        if track is None or not self.eligible: return
        if context['track'] is None:
            context['track'] = track
            self._event(dict(event='UPSTREAM_ENTRY_TRACK_BOUND', track_id=track,
                             line_cycle_id=self.handshake.cycle_id, frame_id=packet['frame_id']))
        if context['track'] != track:
            self._finish_without_frames('ERROR', 'ARRIVING_PRODUCT_IDENTITY_CHANGED', now)
            return
        if not self.handshake.outputs.get('Jetson_InPosition'):
            if not self.handshake.in_position(): return
        if self.handshake.inputs.get('PLC_ConveyorRun'):
            context['conveyor_off_at'] = None
            return
        if context['conveyor_off_at'] is None:
            context['conveyor_off_at'] = now
            return
        # Output OFF is not physical feedback. Existing observed stability plus
        # a source frame captured after the OFF readback are both required.
        if packet['monotonic_s'] <= context['conveyor_off_at'] or not packet.get('stable'): return
        self.request_wait_seconds = self.line_profile['arrival_deadline_s']
        super()._trigger(now)

    def _trigger_legacy(self, now):
        # The installed ladder has no InPosition/ConveyorRun interface. Do not
        # forge one or claim the belt stopped from a visually stable frame.
        if now-self.handshake.accepted_at >= self.line_profile['arrival_deadline_s']:
            reason = ('FIELD_PROFILE_NOT_VERIFIED' if not self._profile_ready()
                      else self.error or 'LEGACY_NO_FRESH_STABLE_PRODUCT')
            self._finish_without_frames('ERROR', reason, now)
            return
        if not self._profile_ready() or self.error or not self.operating:
            return
        context = self.arrival
        if not context or context['preexisting_track'] is not None:
            return
        packet = self.latest_packet
        if not arrival_evidence(packet, self.handshake.accepted_at, context['epoch'],
                                context['generation'], self.zone):
            return
        track = self.coordinator._tracker._track_id
        if track is None or not self.eligible or not packet.get('stable'):
            return
        if context['track'] is None:
            context['track'] = track
            self._event(dict(event='LEGACY_REQUEST_TRACK_BOUND', track_id=track,
                             frame_id=packet['frame_id'], physical_stop_verified=False))
        if context['track'] != track:
            self._finish_without_frames('ERROR', 'ARRIVING_PRODUCT_IDENTITY_CHANGED', now)
            return
        self.request_wait_seconds = self.line_profile['arrival_deadline_s']
        super()._trigger(now)

    def _finish_without_frames(self, decision, reason, now):
        binding = dict(runtime_session_id=self.session_id, cycle_id=None, track_id=None,
            plc_request_token=self.handshake.token,
            plc_contract=getattr(self.gateway, 'contract_version', 'STANDALONE_V3'),
            line_cycle_id=self.handshake.cycle_id, line_session_id=self.handshake.session_id,
            camera_epoch=self.epoch, worker_generation=self.service.generation)
        request = dict(self.service.allocate_request(), kind='inspect', control_mode='production',
                       source_mode='PRODUCTION_AUTO', runtime_binding=binding, view_assessment={})
        identifier, created = self.service.journal.admit(request, self.service.package.snapshot())
        if not created: raise ValueError('DUPLICATE_LINE_DEADLINE_RESULT')
        self.service.journal.finish(identifier, dict(decision=decision, reason=reason,
            reason_code=reason, disposition='HOLD', observations=[], assets=[],
            production_identity=dict(binding, inspection_id=identifier),
            execution=dict(source='not_executed', control='production', worker_generation=self.service.generation)))
        self.handshake.bind(identifier)
        final = dict(decision=decision, existing_decision='NOT_RUN', assembly_decision='NOT_RUN',
                     policy='NO_INPUT_IS_NEVER_PASS', reason=reason)
        self._commit_and_publish(identifier, final, now)

    def _commit_and_publish(self, identifier, final, now):
        row = self.service.journal.detail(identifier)
        binding = ((row or {}).get('request') or {}).get('runtime_binding', {})
        cancelled_error = bool(row and row['state'] == 'CANCELLED'
                               and row['decision'] == final['decision'] == 'ERROR')
        if (not row or (row['state'] != 'COMPLETE' and not cancelled_error)
                or not row['result'].get('storage_success')
                or binding.get('plc_request_token') != self.handshake.token):
            raise ValueError('SAME_REQUEST_DURABLE_COMPONENT_REQUIRED')
        final = dict(final, inspection_id=identifier, line_cycle_id=self.handshake.cycle_id,
            line_session_id=self.handshake.session_id, request_token=self.handshake.token,
            runtime_session_id=self.session_id, completed_monotonic=now,
            track_id=binding.get('track_id'), completed_at=datetime.now(timezone.utc).isoformat(),
            source='INTEGRATED_ACTUAL_INSPECTION', synthetic=False)
        if getattr(self.gateway, 'contract_version', None) == 'LEGACY_THREE_BOOL':
            final.update(plc_contract='LEGACY_THREE_BOOL',
                         ack_scope='WRITE_READBACK_ONLY', plc_consumption_confirmed=False)
        journal = self.service.journal
        with journal.lock, journal.db:
            # INSERT only: a committed final decision is immutable.
            journal.db.execute('INSERT INTO service_state VALUES (?, ?)',
                               ('integrated_decision:'+identifier, json.dumps(final)))
            journal._event('INTEGRATED_FINAL_DURABLE', final)
        self.published_ids.add(identifier)
        self.handshake.publish(identifier, final['decision'], True, time.monotonic())
        entry = dict(final, vision_decision=final['decision'],
            publication_status=self.handshake.publication,
            request_to_publication_ms=(time.monotonic()-self.handshake.accepted_at)*1000)
        self.history.appendleft(entry)
        self.assembly_submitted.pop(identifier, None)
        if len(self.published_ids) > 512:
            self.published_ids = {item['inspection_id'] for item in self.history} | {identifier}
        self._event(dict(event='INTEGRATED_INSPECTION_COMPLETED', **entry))

    def _poll_result(self, now):
        identifier = self.bridge.inspection_id
        if not identifier or identifier in self.published_ids: return
        if self.handshake.cancelled or self.handshake.state != 'INSPECTING':
            self._cancel_pending('LINE_CONTEXT_ENDED')
            return
        issue = getattr(self, 'cycle_issue', None)
        row = self.service.journal.detail(identifier)
        if issue and issue['request_token'] == self.handshake.token:
            if not row or row['state'] not in ('COMPLETE', 'CANCELLED'):
                return  # Existing worker cancellation/timeout owns the raw record.
            self._commit_and_publish(identifier, dict(decision='ERROR',
                existing_decision=row['decision'], assembly_decision='NOT_RUN',
                policy='INVALID_CURRENT_PRODUCT_CONTEXT', reason=issue['reason']), now)
            return
        if row and row.get('state') == 'CANCELLED':
            self._commit_and_publish(identifier, dict(decision='ERROR',
                existing_decision='ERROR', assembly_decision='NOT_RUN',
                policy='CANCELLED_REQUEST_IS_NOT_A_VALID_CLASSIFICATION',
                reason=row['result']['reason']), now)
            return
        updated = self.bridge.poll()
        if updated: self.snapshot = updated
        if self.bridge.error:
            self._fault('DURABLE_BOUNDARY:'+self.bridge.error)
            return
        if self.bridge.phase != 'INSPECTION_DURABLE': return
        row = self.service.journal.detail(identifier)
        try:
            if identifier not in self.assembly_submitted:
                self.assembly_submitted[identifier] = now
                self.assembly.submit(row)
            result = self.assembly.result(identifier)
        except Exception as error:
            result = dict(state='ERROR', reason='ASSEMBLY_EXECUTION:'+type(error).__name__+':'+str(error))
        if result is None and now-self.assembly_submitted[identifier] < self.line_profile['assembly_deadline_s']:
            self.phase = 'ASSEMBLY_INSPECTING'
            return
        if result is None:
            result = dict(state='ERROR', reason='ASSEMBLY_DEADLINE')
        final = combine_decisions(row['decision'], result)
        final['assembly_evidence'] = str(self.assembly.evidence_path(identifier))
        if self.error:
            final.update(decision='ERROR', reason=self.error)
        self._commit_and_publish(identifier, final, now)

    def _acquisition(self, now):
        status = self.service.status()
        if status['ready'] and not self.operating and not self.error:
            self.operating = True  # Software frame acquisition only, never PLC Run.
            self.observation_started_at = now
            self.worker_generation = self.service.generation
            self.service.production_tracking.set()
        if status['state'] == 'RECOVERY' and not status['camera_ready'] and not self.service.active:
            self.line_wait = 'WAIT_CAMERA'
            if now >= self.camera_retry_at and (not self.camera_recovery or not self.camera_recovery.is_alive()):
                self.camera_retry_at = now + 30
                self.camera_recovery = threading.Thread(target=self._recover_camera, daemon=True,
                                                       name='camera-recovery')
                self.camera_recovery.start()

    def _recover_camera(self):
        # Activation can briefly hold the service lock while replacing its child.
        # V3 requires a stopped PLC session. Legacy can only establish an idle
        # request context; it has no physical-stop input or motor command.
        try:
            legacy = getattr(self.gateway, 'contract_version', None) == 'LEGACY_THREE_BOOL'
            if legacy and (self.handshake.token or self.handshake.state not in ('SYNC_LOW', 'ARMED')):
                return
            if not self.handshake.inputs.get('PLC_RunPermit') and not self.service.active:
                self.service.activate(self.service.package.root)
        except Exception:
            self.logger.exception('Camera recovery waits for next bounded attempt')

    def _run(self):
        self.configured.wait()
        while not self.stop.wait(.02):
            with self.lock, self.service.lock:
                if self.closing: continue
                try:
                    now = time.monotonic()
                    self._acquisition(now)
                    self._poll_plc(now)  # Observe the selected contract before any late result.
                    while True:
                        try: packet = self.service.products.get_nowait()
                        except queue.Empty: break
                        self._packet(packet)
                    now = time.monotonic()
                    if self.operating and self.observation_started_at is not None:
                        since = self.latest_packet['processed_monotonic'] if self.latest_packet else self.observation_started_at
                        if now-since > self.observation_stale_seconds:
                            self._fault('CAMERA_OR_OBSERVATION_STREAM_UNAVAILABLE')
                    self._poll_result(now)
                    self._trigger(now)
                except Exception as error:
                    self.logger.exception('Standalone cycle boundary failed')
                    try: self._fault(type(error).__name__+':'+str(error))
                    except Exception:
                        self.error, self.operating = 'JOURNAL_UNAVAILABLE', False
                        self.gateway.close()  # V3 watchdog only; legacy has no heartbeat/stop channel.

    def status(self):
        result = super().status()
        with self.service.journal.lock:
            totals = self.service.journal.db.execute("SELECT json_extract(value,'$.decision'),count(*) "
                "FROM service_state WHERE key LIKE 'integrated_decision:%' GROUP BY 1").fetchall()
        result.update(line_mode=self.line_profile['mode'], line_state=self.line_wait,
            runtime_issue=self.issue, runtime_loop_alive=self.thread.is_alive() and not self.closing,
            final_result_policy='EXISTING_AND_FROZEN_ASSEMBLY_REQUIRED',
            line_profile=self.line_profile, arrival_context=self.arrival,
            actual_motor_feedback='NOT_INSTALLED_COMMAND_AND_VISUAL_STABILITY_ONLY',
            operator_control='PHYSICAL_BUTTONS', laptop_required=False,
            field_acceptance='NOT_RUN', assembly_component=self.assembly.status())
        result['integrated_counts'] = dict.fromkeys(('PASS','FAIL','REVIEW','ERROR'), 0)
        result['integrated_counts'].update(dict(totals))
        if getattr(self.gateway, 'contract_version', None) == 'LEGACY_THREE_BOOL':
            result.update(pusher_control='EXISTING_PLC_UNCHANGED_NO_JETSON_COMMANDS',
                          actual_motor_feedback='NOT_AVAILABLE_IN_EXISTING_CONTRACT',
                          physical_stop_observable=False, plc_consumption_confirmed=False)
        return result

    def close(self):
        with self.lock:
            self.operating = False
            self.handshake.shutdown()
        super().close()
