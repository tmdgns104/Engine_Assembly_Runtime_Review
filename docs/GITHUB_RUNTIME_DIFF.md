# 다섯 버전의 출처 비교

GitHub master commit은 `bb556b4b4aef56f5acb435fce43283aece03533f`. 이번 snapshot 113개 소스 중 master와 63개 동일,26개 다름,24개 없음. laptop과는108개 동일/5개 다름. 이는 113개 검토 범위의 수치이며 전체 저장소 파일 수가 아니다.

|버전|근거|같다고 주장할 수 있는 범위|
|---|---|---|
|GitHub master|GitHub API SHA와 local HEAD 동일, git show로 해당 commit blob 비교|공개 baseline; 현재 standalone 추가기능 다수 없음|
|Jetson 배포본|current source bytes / release.json / 파일hash|engine-dev-28d6e107b0f2a6c3; manifest의 source/config119항목 hash 일치|
|실제 실행본|systemd ExecStart, /proc cmdline/cwd, current path, API identity/traceback|배포경로 실행 확인. Python 메모리 bytecode 전체를 dump/증명한 것은 아님|
|노트북 working tree|원래 repo dirty, 각 같은 상대경로 SHA|pulse latch 등 미배포 코드 포함; 현재 동작으로 간주 금지|
|OpENer 후보|별도 grouped_adapter_009 archive SHA와 C/EDS/검증결과|현재 서비스에 선택/설치되지 않음|

## laptop과 다른 5개

standalone_service.py, omron_cip.py, production_plc.py에는 laptop에만 PULSE_LATCHED 및 별도 Run/Stop 읽기 확장이 있다. 실제 배포 경로는 LEVEL_GUARDED 동작이다. frozen live.py/robustness.py도 laptop 소스와 다르므로 실제 asset 사본을 제공했다. 이번에는 미배포 후보의 정당성/동작을 시험하지 않았다.

## master와 다른 파일

각 SHA와 byte-preservation은 [SOURCE_PROVENANCE](../manifests/SOURCE_PROVENANCE.json), release119대조는 [VERSION_COMPARISON](../manifests/VERSION_COMPARISON.json)을 참조한다. 원본 공개 repo의 uncommitted 변경/branch/remote는 수정하지 않았다.

|검토 파일|master|laptop|
|---|---|---|
|[jetson/boot_live.py](../runtime_source/current/boot_live.py)|DIFFERENT|IDENTICAL|
|[jetson/launch_live.py](../runtime_source/current/launch_live.py)|DIFFERENT|IDENTICAL|
|[jetson/manage_live.py](../runtime_source/current/manage_live.py)|DIFFERENT|IDENTICAL|
|[jetson/standalone_service.py](../runtime_source/current/standalone_service.py)|ABSENT|DIFFERENT|
|[jetson/src/control/omron_cip.py](../runtime_source/current/src/control/omron_cip.py)|DIFFERENT|DIFFERENT|
|[jetson/src/control/plc_v2.py](../runtime_source/current/src/control/plc_v2.py)|ABSENT|IDENTICAL|
|[jetson/src/control/production_plc.py](../runtime_source/current/src/control/production_plc.py)|DIFFERENT|DIFFERENT|
|[jetson/src/control/standalone_plc.py](../runtime_source/current/src/control/standalone_plc.py)|ABSENT|IDENTICAL|
|[jetson/src/integration/clearance.py](../runtime_source/current/src/integration/clearance.py)|DIFFERENT|IDENTICAL|
|[jetson/src/integration/cycle_track_binding.py](../runtime_source/current/src/integration/cycle_track_binding.py)|DIFFERENT|IDENTICAL|
|[jetson/src/integration/provider_tracker_bridge.py](../runtime_source/current/src/integration/provider_tracker_bridge.py)|DIFFERENT|IDENTICAL|
|[jetson/src/journal/sqlite.py](../runtime_source/current/src/journal/sqlite.py)|DIFFERENT|IDENTICAL|
|[jetson/src/observation/area_occupancy.py](../runtime_source/current/src/observation/area_occupancy.py)|DIFFERENT|IDENTICAL|
|[jetson/src/observation/conveyor_occupancy.py](../runtime_source/current/src/observation/conveyor_occupancy.py)|ABSENT|IDENTICAL|
|[jetson/src/observation/conveyor_reference.py](../runtime_source/current/src/observation/conveyor_reference.py)|ABSENT|IDENTICAL|
|[jetson/src/observation/engine_envelope.py](../runtime_source/current/src/observation/engine_envelope.py)|DIFFERENT|IDENTICAL|
|[jetson/src/runtime/bootstrap.py](../runtime_source/current/src/runtime/bootstrap.py)|DIFFERENT|IDENTICAL|
|[jetson/src/runtime/inspection_bridge.py](../runtime_source/current/src/runtime/inspection_bridge.py)|DIFFERENT|IDENTICAL|
|[jetson/src/runtime/logging_support.py](../runtime_source/current/src/runtime/logging_support.py)|DIFFERENT|IDENTICAL|
|[jetson/src/runtime/production.py](../runtime_source/current/src/runtime/production.py)|DIFFERENT|IDENTICAL|
|[jetson/src/runtime/standalone.py](../runtime_source/current/src/runtime/standalone.py)|ABSENT|IDENTICAL|
|[jetson/src/runtime/standalone_web.py](../runtime_source/current/src/runtime/standalone_web.py)|ABSENT|IDENTICAL|
|[jetson/src/tracking/contracts.py](../runtime_source/current/src/tracking/contracts.py)|DIFFERENT|IDENTICAL|
|[jetson/src/tracking/single_active.py](../runtime_source/current/src/tracking/single_active.py)|DIFFERENT|IDENTICAL|
|[jetson/src/vision/assembly_inspection.py](../runtime_source/current/src/vision/assembly_inspection.py)|ABSENT|IDENTICAL|
|[jetson/src/vision/engine_inspector.py](../runtime_source/current/src/vision/engine_inspector.py)|DIFFERENT|IDENTICAL|
|[jetson/src/vision/engine_pose.py](../runtime_source/current/src/vision/engine_pose.py)|DIFFERENT|IDENTICAL|
|[jetson/src/vision/inspection_worker.py](../runtime_source/current/src/vision/inspection_worker.py)|DIFFERENT|IDENTICAL|
|[jetson/src/vision/integrated_decision.py](../runtime_source/current/src/vision/integrated_decision.py)|ABSENT|IDENTICAL|
|[jetson/src/vision/misassembly_shadow.py](../runtime_source/current/src/vision/misassembly_shadow.py)|ABSENT|IDENTICAL|
|[jetson/apps/edge_service/auto_hmi.html](../runtime_source/current/apps/edge_service/auto_hmi.html)|DIFFERENT|IDENTICAL|
|[jetson/apps/edge_service/inspection.html](../runtime_source/current/apps/edge_service/inspection.html)|DIFFERENT|IDENTICAL|
|[jetson/apps/edge_service/inspection.py](../runtime_source/current/apps/edge_service/inspection.py)|DIFFERENT|IDENTICAL|
|[jetson/apps/edge_service/inspection_api.py](../runtime_source/current/apps/edge_service/inspection_api.py)|DIFFERENT|IDENTICAL|
|[jetson/apps/edge_service/inspection_lab.js](../runtime_source/current/apps/edge_service/inspection_lab.js)|DIFFERENT|IDENTICAL|
|[jetson/apps/edge_service/integration_api.py](../runtime_source/current/apps/edge_service/integration_api.py)|DIFFERENT|IDENTICAL|
|[jetson/apps/edge_service/line_hmi.html](../runtime_source/current/apps/edge_service/line_hmi.html)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/absolute_body_seed.py](../runtime_source/frozen_assembly/absolute_body_seed.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/body_motion.py](../runtime_source/frozen_assembly/body_motion.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/live.py](../runtime_source/frozen_assembly/live.py)|ABSENT|DIFFERENT|
|[jetson/shadow_misassembly/live_observation.py](../runtime_source/frozen_assembly/live_observation.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/offline.py](../runtime_source/frozen_assembly/offline.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/policy.py](../runtime_source/frozen_assembly/policy.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/pose_stability.py](../runtime_source/frozen_assembly/pose_stability.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/robustness.py](../runtime_source/frozen_assembly/robustness.py)|ABSENT|DIFFERENT|
|[jetson/shadow_misassembly/robust_preprocessing.py](../runtime_source/frozen_assembly/robust_preprocessing.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/static_geometry.py](../runtime_source/frozen_assembly/static_geometry.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/static_models.py](../runtime_source/frozen_assembly/static_models.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/temporal_models.py](../runtime_source/frozen_assembly/temporal_models.py)|ABSENT|IDENTICAL|
|[jetson/shadow_misassembly/temporal_preprocessing.py](../runtime_source/frozen_assembly/temporal_preprocessing.py)|ABSENT|IDENTICAL|
