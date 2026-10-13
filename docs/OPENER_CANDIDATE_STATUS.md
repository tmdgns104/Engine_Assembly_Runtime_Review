# E. OpENer: 설치본과 격리 후보

근거: [과거 격리 원문](../opener_reference/original_isolated_report.md), [과거 집계](../opener_reference/original_verification.json), [해시/출처](../manifests/OPENER_PROVENANCE.json).

|항목|현재 Jetson 설치본|별도 격리 후보|
|---|---|---|
|Assembly|100Done/101Result 및150Mc_Run/155Stop/157EStop/159Request, 각2B|100Result+Done4B /150Request+EStop+Mc_Run+Stop8B /151Config10B|
|EDS|installed_Engine_Jetson_OpENer.eds|Engine_Jetson_OpENer.eds|
|실행|미실행, hostlistener 없음|이번 실행 안 함; 과거 private namespace에서만 실행|
|Python bridge|없음|없음|
|발행|비활성|Result=0,Done=0 고정; 에코 없음|
|판정|사용자 선택4/8B와 FAIL|HISTORICAL_EVIDENCE: 격리 PASS / 현장 NOT_VERIFIED|

후보 archive SHA256 `de135a52193ac9704616d45a69d03173b2a78f9e4469d2e738b0712a7f79cb5a`를 이번에 다시 계산해 사용자 제시 값과 일치함을 확인했다. archive 자체/ARM64 binary는 업로드하지 않았다.

후보 binary SHA256 `44d8d3f9eade3c3f966e0919cb71cbb7614aa76861128644e42c83e4617b40f2`. 현재 설치 binary SHA256 `f7a4397905470e057f4777dedd4b05916a3826aea60feb7a14c662e5d11be773`와 다르다.

과거 검사: source3/3, ARM64 synthetic24/24, EO path `20 04 24 97 2C 96 2C 64`, RPI50ms, app8+RunIdle4 O→T, app4/modeless T→O, 잘못된 크기/추가 owner 거부, RunIdle/timeout/reconnect, Result/Done 임의 생성 없음. 최신 후보 C와 selected EDS를 참조용으로 포함했다.

Identity Vendor1 / DeviceType12 / Product65001 / Revision2.3 / OpENer PC는 개발 예제 식별값이다. ODVA 인증이나 현장 호환성 인증을 뜻하지 않는다.

미검증: 실제 PLC ForwardOpen, PLC의 BOOL wire encoding, 스위치 multicast/RPI, 실제 결과/완료 소비, Python IPC 및 서비스 소유자 전환. 실행만 켜도 이 부분이 완성되는 것은 아니다.

현재 작업은 설치·실행·승격·후속 bridge 구현을 하지 않았다. 후보 보고서 속 PID1078은 당시 값이며 이번 운영 PID1082와 구분한다.
