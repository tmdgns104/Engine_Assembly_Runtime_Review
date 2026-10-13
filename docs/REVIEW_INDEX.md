# H. ChatGPT 검토 안내

이 저장소를 GitHub 연결 앱에 허용한 뒤 다음 요청으로 검토할 수 있다. 연결 권한/색인 여부가 확인되지 않으면 안전 검토 ZIP 또는 필요한 파일을 직접 제공한다.

> 이 저장소는 2026-10-13 Jetson 실제 운영본의 읽기 전용 snapshot이다. README와 CURRENT_RUNTIME, CURRENT_UI, KNOWN_ISSUES부터 읽어라. VERIFIED_RUNTIME과 SOURCE_ONLY, 과거 격리 PASS를 구분하라. 운영 소스/PLC를 바꾸지 말고, START→sensor→검사 위치 정지→실제 검사→Result/Done→PLC 소비→다음제품 사이클을 막는 원인과 최소 수정 순서를 검토하라. 모델 재학습이나 새 통신계약을 먼저 제안하지 말고, 현재 선택한 4/8/10B 단일 EO 계약을 기준으로 하라.

|순서|문서/소스|핵심 질문|
|---|---|---|
|1|README / CURRENT_RUNTIME / CURRENT_UI / KNOWN_ISSUES|살아 있는 기능과 차단된 기능은 무엇인가?|
|2|GITHUB_RUNTIME_DIFF + SOURCE_PROVENANCE|검토 중인 코드가 실제 배포본인가?|
|3|standalone_service.main / bootstrap.build_runtime|LEGACY와 필수 Assembly가 실제로 선택되는가?|
|4|standalone._run, _observation_issue / production._event|TypeError와 영구 FAULT 경계의 원인은 무엇인가?|
|5|standalone._trigger_legacy / production._trigger / inspection_bridge.submit_production,poll|현재 제품/새frame/request token을 제대로 연결하는가?|
|6|inspection.InspectionService.submit,_monitor_loop / inspection_worker.worker_main / Journal.finish|결과가 durable commit된 뒤에만 쓰는가?|
|7|assembly_inspection.AssemblyInspector / misassembly_shadow.process_one / integrated_decision.combine_decisions|cold-start/3frame/기존+신규 결과 의미가 일치하는가?|
|8|production_plc.LegacyStandaloneHandshake / omron_cip.LegacyStandaloneGateway|Request OFF/STOP/duplicate/readback/소비를 구분하는가?|
|9|PLC_INTEGRATION / OPENER_CANDIDATE_STATUS / candidate_sampleapplication.c / EDS|cyclic bridge 최소변경과 단일 writer 전환을 어떻게 검증할 것인가?|

경로는 `runtime_source/current/` 아래이며 frozen 모델 처리 소스는 `runtime_source/frozen_assembly/`다. [함수와 줄번호](../manifests/SYMBOL_INDEX.json)에서 찾을 수 있다.

## 바로 여는 주요 소스

- [standalone_service.py](../runtime_source/current/standalone_service.py): `main` / 실제 contract·assembly 선택
- [bootstrap.py](../runtime_source/current/src/runtime/bootstrap.py): `build_runtime` / worker·runtime 구성
- [standalone.py](../runtime_source/current/src/runtime/standalone.py): `StandaloneRuntime._run`, `_observation_issue`, `_trigger_legacy`, `_poll_result`, `_commit_and_publish`
- [production.py](../runtime_source/current/src/runtime/production.py): `ProductionRuntime._event`, `_trigger`, `_apply_packet`
- [inspection_bridge.py](../runtime_source/current/src/runtime/inspection_bridge.py): `InspectionBridge.submit_production`, `poll`
- [inspection.py](../runtime_source/current/apps/edge_service/inspection.py): `InspectionService.submit`, `_monitor_loop`
- [inspection_worker.py](../runtime_source/current/src/vision/inspection_worker.py): `worker_main` / 새 프레임 검사
- [assembly_inspection.py](../runtime_source/current/src/vision/assembly_inspection.py)와 [integrated_decision.py](../runtime_source/current/src/vision/integrated_decision.py): 필수 조립 검사와 `combine_decisions`
- [sqlite.py](../runtime_source/current/src/journal/sqlite.py): `Journal.finish` / 영속 저장
- [production_plc.py](../runtime_source/current/src/control/production_plc.py)와 [omron_cip.py](../runtime_source/current/src/control/omron_cip.py): `LegacyStandaloneHandshake`, `LegacyStandaloneGateway`
- [standalone_web.py](../runtime_source/current/src/runtime/standalone_web.py), [integration_api.py](../runtime_source/current/apps/edge_service/integration_api.py), [auto_hmi.html](../runtime_source/current/apps/edge_service/auto_hmi.html), [line_hmi.html](../runtime_source/current/apps/edge_service/line_hmi.html): 실제 UI/API 표시와 요청 차단
- [후보 C](../opener_reference/candidate_sampleapplication.c), [callback](../opener_reference/engine_callbacks.c.inc), [EDS](../opener_reference/Engine_Jetson_OpENer.eds): 현재 운영본과 분리된 격리 후보

검토 결과에는 (1) 재사용할 구현, (2) 반드시 수정할 결함, (3) PLC 온라인 비교 필요 항목, (4) 실제 현장 시험에서만 검증할 항목을 분리해 달라. mock/격리/native 합성 PASS를 현장 cycle PASS로 합치지 말라.

의도적으로 없는 자료: 가중치·학습/평가 이미지·E04·원본 운영 DB/이력·비밀값·바이너리. 이 자료가 없어 모델 정확도나 실물 동작을 독립 재현할 수 없다는 한계를 유지한다.
