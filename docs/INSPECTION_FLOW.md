# 실제 request → 결과 흐름

아래는 **VERIFIED_SOURCE_ONLY** 경로다. 이번에는 현장 request를 만들거나 검사를 실행하지 않았다. 현재 오류/설정으로 완주하지 못한다.

1. `StandaloneRuntime._run` → `_poll_plc` → `_poll_legacy_plc` → `LegacyStandaloneHandshake.poll` → `OmronCipGateway.read_request` → `_read_bool('Inspection_Request')`. PLC 44818 TCP RegisterSession/SendRRData CIP 0x4C를 사용한다. cyclic input을 읽는 것이 아니다.
2. 초기 probe는 Request/Result/Done 세 BOOL의 타입과 값 확인. 시작 시 Request 또는 Done 잔여 ON이면 HOLD. 유효 LOW 이후 상승 edge에 UUID request token, accepted_at을 만들고 REQUEST_LATCHED가 된다.
3. `_trigger_legacy`는 현장 profile, 동일 camera epoch/worker generation, 요청 이후 새 packet, product 1개, 전체 bbox의 zone 내부, eligible/stable, preexisting_track 없음 등을 검사한다. sensor→camera 시간은 현장 PLC의 역할이다. legacy에는 ConveyorRun/정지 feedback가 없어 실제 벨트 정지를 알 수 없다.
4. `ProductionRuntime._trigger`는 제품/Track/cycle/request token/epoch/generation을 binding에 묶고 `InspectionBridge.submit_production` → `InspectionService.allocate_request/submit`을 호출한다. Journal.admit가 ACCEPTED를 저장하고 command queue에 active job을 보낸다.
5. `inspection_worker.worker_main`이 실제 카메라의 새 frame을 선택한다. freshness/quality/deadline/cancellation/production binding 확인 후 기존 detector/pose/slot 검사, `assess_dynamic`를 수행한다. 실제 `result` dict와 `images`를 `results.put({'type':'result', 'generation', 'inspection_id', 'result', 'images'})`로 전달한다. preview는 이 결과와 분리되어 있다.
6. `InspectionService._monitor_loop`가 generation/active identity/deadline을 확인한다. 늦은 결과는 quarantine. `Journal.finish`가 raw와 이미지, SHA, request/결과/defect/event/outbox를 저장하고 COMPLETE/storage_success=true를 만든다. SQLite WAL/synchronous FULL. Journal은 PLC를 쓰지 않는다.
7. `InspectionBridge.poll`은 COMPLETE, storage_success, inspection identity, request, package, worker generation, production binding의 일치를 확인해 INSPECTION_DURABLE로 전환한다.
8. `StandaloneRuntime._poll_result`는 같은 저장 raw를 `AssemblyInspector.submit`에 보낸다. `ShadowObserver.process_one`은 raw 파일/decoded pixel hash/frame metadata 확인, 제품마다 guard.reset, 현재 raw로 cold-start 정렬·crop·네 분류기·ThreeFrameObservation을 수행한다. 현재 클래스명이 ShadowObserver여도 실행 subclass의 mode는 REQUIRED_FINAL_COMPONENT다.
9. `combine_decisions`가 기존 결과와 조립 3-frame 결과를 결합한다. `_commit_and_publish`는 동일 request의 durable component를 확인하고 `service_state['integrated_decision:'+id]`를 INSERT 및 event 기록한 뒤 `handshake.publish`를 호출한다.
10. publish가 허용된 PASS/FAIL이면 Result write/readback 후 Done=True write/readback 순서다. 해당 상태는 WRITE_READBACK_ONLY이며 PLC ladder의 소비 ACK가 아니다. 이후 Request LOW에 Done=False, 영상 product_clear+태그 idle을 확인한 후 다음 cycle을 연다.

## 현재 결합 판정표

조립 COMPLETE의 PASS_CANDIDATE→PASS, FAIL_CANDIDATE→FAIL. 조립 ERROR→ERROR, 기타 미완료/자료부족→REVIEW. 최종 우선순위는 ERROR > REVIEW > FAIL > PASS.

|기존 검사 ↓ / 조립 →|PASS|FAIL|REVIEW|ERROR|
|---|---|---|---|---|
|PASS|PASS|FAIL|REVIEW|ERROR|
|FAIL|FAIL|FAIL|REVIEW|ERROR|
|REVIEW|REVIEW|REVIEW|REVIEW|ERROR|
|ERROR|ERROR|ERROR|ERROR|ERROR|

`integrated_decision.py:combine_decisions`에서 직접 확인했다. 이번에는 모델/프로그램 실행 시험을 반복하지 않았다. 정상이라는 사람 선언을 모델 입력/결과 보정에 사용하지 않는다.

## 현재 제약

- legacy Request OFF는 `_request_withdrawn`에서 WAIT_PRODUCT_CLEAR/BLOCKED로 넘어가며 `_cancel_pending`이 검사 취소를 요청한다. 짧은 sensor pulse를 끝까지 처리하는 후보는 laptop에 있지만 현재 배포본에는 없다.
- REVIEW/ERROR는 legacy `publish`에서 NOT_SENT로 보류한다. UI에 ERROR가 보인다는 것과 PLC가 결과를 받았다는 것은 다르다.
- 새 제품마다 absolute seed를 다시 필요로 하므로 cold-start 정렬 REVIEW는 남은 검증 항목이다. 연속 정상300 이력만으로 이 경계를 통과했다고 할 수 없다.
- ThreeFrameObservation은 timestamp/ID뿐 아니라 같은 pixel hash도 중복으로 취급한다. 실제 새 정지 frame의 동일 픽셀에 대한 제한은 source-only로 확인했으며 이번 수정 대상이 아니다.

핵심 파일은 [runtime source](../runtime_source/current/)와 [frozen assembly](../runtime_source/frozen_assembly/)에 원문 그대로 있다.
