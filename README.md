# Jetson 엔진 검사 시스템 — 실제 운영본 검토

**2026-10-13 읽기 전용 조사. 자료 확보·정적 분석은 완료했지만, 자동 검사라인은 정상 동작 완료 상태가 아니다.**

현재 `engine-dev-28d6e107b0f2a6c3`의 systemd·웹·카메라·모델은 살아 있다. 그러나 상위 runtime은 `monotonic_s` TypeError로 FAULT/RESYNC_REQUIRED이며 결과 쓰기는 설정에서 꺼져 있다. 현재 사용 경로는 Python Explicit Messaging `LEGACY_THREE_BOOL`이다. OpENer 4/8B 후보는 격리 검증만 통과했고 설치·현장 실행·Python bridge는 아직 완료되지 않았다.

## 먼저 읽기

1. [검토 순서와 질문](docs/REVIEW_INDEX.md)
2. [현재 실행 상태](docs/CURRENT_RUNTIME.md) → [UI와 API](docs/CURRENT_UI.md)
3. [구조](docs/CURRENT_ARCHITECTURE.md) → [실제 검사 호출 흐름](docs/INSPECTION_FLOW.md)
4. [PLC 통합의 8가지 답변](docs/PLC_INTEGRATION.md) → [OpENer 후보](docs/OPENER_CANDIDATE_STATUS.md)
5. [차단 원인](docs/KNOWN_ISSUES.md) → [다섯 버전 비교](docs/GITHUB_RUNTIME_DIFF.md)

## 이 저장소의 성격

- `runtime_source/current/`: Jetson 실제 배포 소스 100개를 원문 바이트로 보존했다. 운영 진입점, 이전 수동/진단 코드가 함께 들어 있다. 모든 파일이 현재 실행 경로라는 뜻은 아니다.
- `runtime_source/frozen_assembly/`: 현재 로더가 `assets/misassembly_runtime`에서 불러오는 Python 소스 13개. 코드가 `current` 밖에 있어 별도로 분리했다.
- `config_reference/`: 비밀값 없는 읽기용 설정 사본/요약. 설치 파일이나 실행 권고가 아니다. 환경변수 파일은 제외했다.
- `opener_reference/`: 기존 격리 후보와 설치본을 구분한 C/EDS/프로파일/과거 보고서. 실행 파일은 없다.
- `manifests/`: 출처·SHA-256·버전 대조·API 관측·검증 범위.
- `screenshots/`: `/auto`, `/line`, 유지보수 상단. 제품 모형만 보이며, 유지보수의 과거 검사 이력은 공유에서 제외했다.

모델·TensorRT 엔진·원본 DB·검사 이미지 이력·비밀키·토큰·E04·학습 자료를 포함하지 않는다. **실행 가능한 전체 배포 패키지가 아니다.** 이 자료만으로 프로그램을 실행하거나 PLC 쓰기를 활성화하지 않는다.

## 근거 수준

|표기|의미|
|---|---|
|VERIFIED_RUNTIME|이번 읽기 전용 OS/API/화면 관측|
|VERIFIED_SOURCE_ONLY|확보한 실제 소스에서 확인; 해당 기능 실행 시험은 아님|
|HISTORICAL_EVIDENCE|기존 보고서/시험 결과 재사용; 이번에 재시험하지 않음|
|NOT_IMPLEMENTED|현재 실행 경로에 기능이 없음|
|FAILED|관측된 오류 또는 요구와 불일치|
|NOT_VERIFIED|현장 동작·온라인 PLC 적용·장기 운전 등 미검증|

기존 공개 저장소 master `bb556b4b4aef56f5acb435fce43283aece03533f`와 이 자료는 다르다. 기존 공개 저장소·운영 소스·PLC·서비스·모델은 변경하지 않았다. 버튼을 누르거나 시험 결과를 송신하지 않았다.

ChatGPT GitHub 앱에서 이 **비공개 저장소의 접근 권한과 색인 가능 여부를 별도로 확인**해야 한다. URL 제공만으로 ChatGPT 접근 성공을 뜻하지 않는다.

## 자료 검증

[공유 전 검사](manifests/SHARING_AUDIT.json): Python은 import/실행 없이 AST 문법을 검사했고 JSON·문서 링크·소스 원문 해시·민감정보 패턴·파일 종류를 확인했다. 사진 3장은 실제 확인했으며 개인과 과거 검사 이력을 제외했다. 이 검사는 프로그램 기능/AI 정확도 시험이 아니다.

[종료 전 보존 확인](manifests/FINAL_PRESERVATION.json): 선택 소스·설정·설치 OpENer 등 125개 파일의 해시가 조사 시작 때와 같았다. MainPID1082, NRestarts0, boot ID·runtime session도 유지됐다. PID2790이 실제 `/dev/video0`을 열고 있었으며 새 frame은 갱신되지만 상위 TypeError는 남아 있었다.
