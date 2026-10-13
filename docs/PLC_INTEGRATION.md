# D. PLC 통합 — 8가지 질문

## 1. Request는 어디서 받는가?

현재 `omron_cip.py:OmronCipGateway.read_request/_read_bool`가 PLC192.168.50.3에 직접 Explicit CIP 0x4C로 Inspection_Request BOOL을 읽는다. local192.168.50.2/enP8p1s0이다. `standalone_service.py`의 plc_contract는 LEGACY_THREE_BOOL. OpENer Assembly150이 입력되는 경로는 없다.

## 2. 요청이 오면 어떤 함수가 실행되는가?

`StandaloneRuntime._poll_legacy_plc` → `LegacyStandaloneHandshake.poll` → Request edge/token → `_trigger_legacy` → `ProductionRuntime._trigger` → `InspectionBridge.submit_production` → `InspectionService.submit` → worker queue. 현재 FAULT/RESYNC이므로 이 경로 완주를 관측하지 않았다.

## 3. 결과는 어떤 객체로 전달되는가?

worker result message의 `inspection_id`, `generation`, `result` dict, `images`; Journal row의 `decision`, `result.storage_success`, `request.runtime_binding`; AssemblyInspector result JSON의 `state`, `frames`, `three_frames`; `combine_decisions`의 `final['decision']`. 최종 결과는 service_state `integrated_decision:{id}`에 고정된다.

## 4. Journal 저장 후 누가 발행을 결정하는가?

`InspectionBridge.poll`이 동일 request의 durable 결과를 검증하고, `StandaloneRuntime._poll_result/_commit_and_publish`가 필수 조립 검사까지 결합한다. 이후 `LegacyStandaloneHandshake.publish`가 cycle/상태/durability와 표현 가능한 판정을 검사하며 gateway의 writes_enabled/contract_verified가 마지막 쓰기 문턱이다. Journal.finish가 곧 PLC 전송은 아니다.

## 5. Result/Done은 누가 만드는가?

`RequestHandshake.publish`가 PASS=False/FAIL=True Result를 계산하고, `OmronCipGateway.write_result/_write_bool`(CIP0x4D)로 쓴 뒤 readback 확인, 다음 Done=True를 쓴다. Request LOW 후 Done=False. 현재 legacy는 REVIEW/ERROR를 이 BOOL에 강제 매핑하지 않고 NOT_SENT로 남긴다. 설정 false이므로 지금 실제 발행은 비활성이다.

OpENer 후보 C callback은 두 결과 슬롯을0으로 유지한다. 검사 프로그램 연결이 없으므로 Done=0/Result=0을 PASS로 해석하면 안 된다.

## 6. Explicit/Cyclic 중복 위험

두 발행자를 동시에 켜면 PLC Input tag가 cyclic 값으로 덮이거나, Explicit Done reset과 cyclic Done이 경쟁하고, 서로 다른 cycle 결과/완료가 섞일 수 있다. 현재는 OpENer 미실행·Explicit 쓰기 false라 **활성 중복 발행은 관측하지 않았다**. 미래 전환 시 단일 결과 소유자/세션·cycle 경계·재접속 유효성·중복 발행 방지가 필요하다. 단순 서비스 둘 동시 실행으로 해결하지 않는다.

## 7. 최소 변경 위치 — 제안만, 이번 미구현

1. OpENer candidate callback과 Python 사이의 명시적 IPC: 수신8B·연결세션·Run/Idle·sequence·age, 송신4B의 원자적 snapshot과 결과 유효성. 현재 진단 JSON은 결과 bridge가 아니다.
2. gateway adapter 및 entrypoint transport 선택: `standalone_service.py`, `src/control/…`. 새 cyclic 경로 선택 시 explicit 결과 writer를 끄는 상호 배타 조건.
3. handshake와 runtime binding: Request latch/독립 Run·Stop·EStop 근거/한 제품 한 결과/Done 유지·reset/불명확 ACK/late result 처리. `production_plc.py`, `standalone.py`의 현 상태를 기준으로 검토.
4. Journal commit 이후 `final`을 bridge에 전달. 기존 비전 worker/모델/threshold를 통신 변경 때문에 새로 만들 필요는 없다.
5. UI의 transport·connection age·실제 발행/소비 구분. 이번에는 설계 확정·코드 작성·테스트·배포하지 않았다.

## 8. 기존 PLC 래더를 유지할 수 있는가?

**통신 매핑은 기존 6개 신호로 유지할 가능성이 있지만, 전체 반복공정 보장은 미확인이다.** 사용자 선택 파일은 “푸셔없는버전3”이며 과거 STANDALONE_V3 신규 계약과 다른 이름이다.

기존 저장본 검토([원문 참고](../opener_reference/PLC_BASELINE_REVIEW.md), HISTORICAL_EVIDENCE): NX1P2-9024DT1, IP192.168.50.3, Move_Timer T#2.7s; sensor→Move_pending→Inspecting/컨베이어출력OFF→Request유지→Done/Result 소비→검사해제. 23개 rung/6개 공개 BOOL. 원본 hash `9f491ee447dd5736858d07d2174a033a1654501b18f4c53fa641b4bf29b97806`.

이번에는 온라인 PLC 전체 프로그램과 저장본이 같은지 대조/다운로드하지 않았다. 2.7초의 실제 도착·정지 적합성, STOP 때 Move_pending 잔여, 검사 timeout, REVIEW/ERROR 전달 방식, NG 공통 배출/다음제품 준비는 미검증이다. 기존3BOOL에는 cycle ID/명시 소비 ACK/Ready/Heartbeat가 없다. Output OFF나 Result readback을 물리 정지/소비로 간주하지 않는다.

## 사용자 선택 cyclic 계약

|Assembly|방향|바이트와 예상 순서|
|---|---|---|
|100|Jetson→PLC,4B|0–1 Result,2–3 Done|
|150|PLC→Jetson,8B|0–1 Request,2–3 EStop_OK,4–5 Mc_Run,6–7 Stop_PB|
|151|Config,10B|연결 configuration|

Exclusive Owner 하나, RPI50ms, PLC Input Multicast/Output P2P. 실제 BOOL bit/padding/endian은 NOT_VERIFIED. 일반 EtherNet/IP를 안전 회로나 비상정지의 대체로 삼지 않는다.
