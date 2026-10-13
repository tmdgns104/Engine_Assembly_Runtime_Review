# F. 전체 검사라인을 막는 문제

## 1. 관찰 오류 기록이 상위 runtime을 FAULT로 만든다 — FAILED

이번 runtime/status, /auto, /line에 `TypeError:dict() got multiple values for keyword argument 'monotonic_s'`가 남아 있고 RESYNC_REQUIRED/BLOCKED다. 2026-10-13 15:48:26 KST runtime.log traceback을 코드와 대조했다. 과거 오류만 재인용한 것이 아니다.

호출: `StandaloneRuntime._run`(474) → `ProductionRuntime._packet`(391)/`_apply_packet`(480) → `_fault('MULTIPLE_PRODUCT_AMBIGUITY')` → `StandaloneRuntime._observation_issue`(72) → `_event`(83) → `ProductionRuntime._event`(84–89).

`self.issue`에 monotonic_s가 들어 있는데 `dict(runtime_session_id=…, monotonic_s=time.monotonic(), …, **value)`가 같은 keyword를 다시 넣는다. 이 예외는 dict 생성 단계에서 발생하므로 해당 event 저장/그 뒤 preview 재획득이 완료되지 않는다. `_run`은 예외를 잡아 fault를 남기지만 loop/process는 살아 있다. 따라서 시스템 active와 검사 사이클 성공은 다르다.

추가 정적 위험: `_commit_and_publish`의 final에는 runtime_session_id가 포함되고, 이를 `_event(dict(event=…, **entry))`에 전달한다. 같은 방식으로 runtime_session_id 중복 keyword가 발생할 수 있다. 현재 완료검사0이라 이 두 번째 예외는 **VERIFIED_SOURCE_ONLY / 현장 발생 NOT_VERIFIED**다. 이번에 재현을 위해 검사를 만들지 않았다.

## 2. 실제 결과 송신 비활성 — VERIFIED_RUNTIME

config `legacy_publication_enabled=false`; gateway/runtime/status도 false. Release API의 true는 check_files에서 plc_bench 여부를 정적으로 기록한 값이다. 현재 writes false를 우선한다. 오류만 제거해도 자동 발행되는 상태가 아니다.

## 3. 선택한 cyclic 계약은 운영에 연결되지 않았다

설치 OpENer는 구2B 분리형, 실행 안 됨. 4/8B 후보는 노트북에 보존돼 있고 Python bridge는 NOT_IMPLEMENTED. 현장 PLC I/O/소비 성공 근거 없음.

## 4. 현장 검사/이탈 프로파일과 코드 경로 불일치

`field_profile_verified=false`라 `_profile_ready`가 false다. 현재 zone은 x0.2–0.8/y0.65–0.9인 반면 profile의 observed_capture_zone은 전체화면이다. runtime은 Journal의 zone을 가져오며 profile의 observed_capture_zone을 자동 적용하지 않는다. 현재 엔진 bbox의 높이/위치가 작은 active zone에 완전히 들어오지 않는다. 배치를 바꾸거나 gate를 해제하지 않았다.

설치 `area_clearance.json`의 mode는 CONVEYOR_FROZEN_EMPTY_ENVELOPE다. bootstrap은 real gateway일 때 DARK_SURFACE_SELF_OBSERVED 또는 CONVEYOR_DARK_BELT_SELF_OBSERVED만 area_version으로 허용한다. 관측에서 area_clearance_enabled=false, area_reference_approved=false, area_observation_valid=false였다. Worker 측 area classification은 UNKNOWN이었다. 이미지 기반영역모델이 존재하는 것과 production clearance에 승인된 것은 다르다.

## 5. Request OFF와 실제 STOP을 구분하지 못하는 배포본

현재 legacy read allowlist는 Request/Result/Done뿐이다. `_request_withdrawn`이 검사 출력 차단으로 처리한다. laptop의 PULSE_LATCHED/read_run_context 후보는 운영본에 없으며 배포/채택하지 않았다. 사용자 선택PLC 저장본의 Request유지 로직과 실제 온라인 상태의 일치도 추가 확인이 필요하다.

## 6. 결과 소비·불확실 판정·반복 운전 미완료

Result/Done write readback은 소비 ACK가 아니다. REVIEW/ERROR는 legacy에서 NOT_SENT, 명시적 cycle ID/Ready/Heartbeat 없음. 현재 저장본의 timeout/STOP 잔여/NG 배출은 현장 미검증이다. 통신 연결만으로 전체 자동공정 성공이라고 할 수 없다.

## 7. UI 오해 가능성

V3 고정문구, SHADOW 전용문구, Release writes=true, root 하위ready 표시는 현재 실제 계약/상위fault/필수분류정책과 다르다. 활성처럼 보이는 POST 버튼도 standalone middleware로 차단된다. `CURRENT_UI.md`에 각각 근거를 남겼다.

## 8. AI 정확도와 cold-start

Assembly required 경로는 제품마다 pose를 초기화한다. 정상300의 연속 조건과 다르며 cold-start REVIEW가 남은 검증 항목이다. 이번에는 모델 정확도·검사 지연·300/590/155 반복 검증을 실행하지 않았다. TRACKING_ONLY preview의 REVIEW는 제품 최종 REVIEW로 집계하지 않는다.

다음 개발의 검토 우선순위 제안: 이벤트 기록 충돌 → 실제 현장 profile/도착·정지·이탈 계약 → single-writer cyclic bridge와 불확실 결과 정책 → 읽기 표시 정합성 → 승인된 현장 한 사이클/반복/재부팅/노트북OFF. 이번 작업에서는 어느 수정도 실행하지 않았다.
