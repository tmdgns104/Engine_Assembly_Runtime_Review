# OpENer 4/8바이트 계약 수정 및 격리 검증

최종 상태: **COMPLETE_ISOLATED_PASS**. 격리 후보의 소스 계약 검사 3개와 ARM64 합성 Originator 검사 24개가 통과했다.
실제 PLC I/O는 **NOT_RUN**, PLC BOOL 인코딩은 **UNVERIFIED**, Python 검사 bridge는 **NOT_IMPLEMENTED**다.
운영 설치본과 기존 검사 서비스는 교체·재시작하지 않았다.

작성 시각: 2026-10-13T06:28:41.346761+00:00
기존 Task ENGINE-STANDALONE-PLC-AUTOSTART-001의 동일 run/tag_data_link_008 안에서 수행했다.
이번 사용자 지시의 통신 수정·격리 검증 범위를 적용했다. 과거 root STATUS의 독립 2B 태그 안내는
이번 선택한 4/8B 계약의 근거로 사용하지 않았으며, root 문서는 변경하지 않았다.

## 1. 변경 전후

|항목|현재 설치본: 그대로 유지|격리 후보|
|---|---|---|
|프로파일|EXISTING_PLC_SEPARATE_BOOL_DISARMED|SELECTED_PLC_GROUPED_4_8_COMMUNICATION|
|입력: Jetson→PLC|100 Done 2B, 101 Result 2B|100 Result + Done 4B|
|출력: PLC→Jetson|150 Mc_Run, 155 Stop_PB, 157 EStop_OK, 159 Request 각각 2B|150 Request + EStop_OK + Mc_Run + Stop_PB 8B|
|Configuration|151, 10B|151, 10B|
|응용 연결|분리된 6개 태그 연결|100/150 한 쌍의 Exclusive Owner|
|RPI|이전 프로파일 30ms|시험에서 50ms 요청·응답 확인|
|검사 결과 발행|비활성|비활성, Result=0 / Done=0|

현재 설치본은 이 사용자의 묶음 계약과 여전히 다르다. 이번 PASS는 운영 설치본 교체를 뜻하지 않는다.
기본 upstream의 32/32B 소스에서 새 후보를 생성했으며, 예전 잘못된 태그 순서의 4/8B 백업을 복원하지 않았다.

예상 바이트 배치(실제 PLC wire 확인은 별도):

|Assembly|Offset|변수|크기|
|---|---:|---|---:|
|100|0–1|Jetson_Result|2B|
|100|2–3|Jetson_Done|2B|
|150|0–1|Inspection_Request|2B|
|150|2–3|EStop_OK|2B|
|150|4–5|Mc_Run|2B|
|150|6–7|Stop_PB|2B|

후보 진단은 150을 little-endian 16비트 네 슬롯으로 읽는다. 0/1 외 값은 원문 그대로 남기고
bool_slots_valid=false로 표시한다. 이것은 예상 인코딩 검증이며 실제 OMRON BOOL 인코딩을 확정한 것이 아니다.
100의 두 슬롯은 아직 모두 0으로 유지되므로 독립적인 Result/Done 비트 전송은 다음 bridge 시험 대상이다.
**Done=0인 0/0은 검사 미완료이며 PASS를 뜻하지 않는다.**

## 2. 변경 파일

모든 최종 수정은 이 격리 폴더 안에만 있다.

- work/notebook/deployment/opener/prepare_profile.py: 핀 고정 소스로 4/8/10B 생성, 선택 EDS 해시 검증·그대로 복사.
- work/notebook/deployment/opener/engine_callbacks.c.inc: 에코 제거, 미완료 출력 유지, 입력 슬롯·연결·Run/Idle 진단.
- work/notebook/deployment/opener/build_on_jetson.py: 검증된 캐시 libcap-dev를 scratch에만 추출; 다운로드·전역 설치 없음.
- work/notebook/tests/test_opener_plc_profile.py: 크기·순서·EDS 불변성 검사.
- work/probe_grouped.py, run_isolated.sh, prepare_private_network.py: 제한시간이 있는 격리 합성 Originator.
- native_verified/profile/source/src/ports/POSIX/sample_application/sampleapplication.c: 실제 빌드한 최종 C 소스.
- OPENER_SOURCE.diff: 핀 고정 upstream 대비 최종 코드 변경.

범위가 좁혀지기 전 canonical 도구에 작성했던 수정은 격리 work로 회수한 뒤 수정 전 바이트로 복원했다.
SOURCE_ISOLATION.json 및 RETRIEVAL_VERIFICATION.json으로 기존 도구와 선택 EDS 보존을 재확인했다.
기존 검사 코드·PLC 게이트웨이·모델·PLC 프로그램·Sysmac 설정은 변경하지 않았다.

## 3. EDS와 구현

선택 EDS SHA256: 78c0a78cb4f3e43da8090d41cdddfa14aa86dac7212f229104c0e75f02071b01
native_verified/profile/Engine_Jetson_OpENer.eds는 원본과 바이트 단위로 같다.

- Exclusive Owner 경로: 20 04 24 97 2C 96 2C 64 (config151, consumed150, produced100).
- Config 데이터 10B가 포함된 Forward Open 성공; 8B config 요청 거부.
- Identity: Vendor 1 / Device Type 12 / Product 65001 / Revision 2.3 / OpENer PC.
- Identity는 선택 EDS와 같은 upstream 개발용 식별값이다. 프로젝트 전용 ODVA 할당·인증 주장이 아니다.
- EDS Connection1 값 0x84010002 / 0x44640405를 보존했다.
- O→T: Point-to-Point, app8 + Run/Idle4 + Class1 sequence2 = connected data14B.
- T→O: Multicast, app4 + Class1 sequence2 = connected data6B; Run/Idle header 없음.
- UDP encapsulation/address item 크기를 Assembly 크기에 포함하지 않는다.
- RPI 요청·응답 50000μs; timeout multiplier=0, RPI×4. EDS 기본값30ms는 50ms 사용을 막지 않으며 변경하지 않았다.

선택 EDS의 Input Only/Listen Only 및 upstream의 보조 heartbeat/explicit Assembly 정의는 보존했다.
이번 검증·사용 대상은 단일 Exclusive Owner 경로다. 두 번째 Exclusive Owner는 실제 거부됐다.
보조 연결 정의의 현장 사용은 검증 범위가 아니다.

## 4. 격리 빌드·시험

환경: aarch64, kernel 5.15.148-tegra, cc (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0, cmake version 3.22.1, bubblewrap 0.6.1.
컴파일·링크 성공, ldd의 missing library 없음.
후보 binary SHA256: 44d8d3f9eade3c3f966e0919cb71cbb7614aa76861128644e42c83e4617b40f2

bwrap의 별도 user/PID/network namespace에서만 실행했다. 프로브가 host와 다른 network namespace 및
lo 인터페이스 하나만 존재함을 확인했다. 루트 파일시스템은 읽기 전용, 쓰기 허용은 해당 scratch와 임시 영역뿐이다.
Multicast를 위해 새 namespace 안의 lo와 224/4 경로만 설정했다. CAP_NET_ADMIN은 새 user/network namespace에만 적용했다.
enP8p1s0와 현장 PLC 주소에는 연결하지 않았다. 시험 전체 제한55초, 자체 종료·정리를 사용했다.

|검사|결과|
|---|---|
|소스 계약 단위 검사|3 PASS|
|실제 ARM64 identity / Assembly 크기|PASS|
|EO Forward Open / Config10 / RPI50ms|PASS|
|P2P 생산 진단 및 Multicast 생산|모두 PASS|
|각 연결의 16가지 0/1 네 슬롯 조합|모두 위치·원문·값 일치|
|16패턴 구간 실제 수신 sequence 수|P2P 65, Multicast 65|
|구 2B·32B 연결 크기, 잘못된 인스턴스·config8B|거부 PASS|
|두 번째 Exclusive Owner|거부 PASS|
|6B·10B의 잘못된 cyclic app 데이터|기존 8B 입력을 바꾸지 않음 PASS|
|0x0100·0xFFFF 예상 BOOL 범위 외 값|값 보존·invalid 표시 PASS|
|Run/Idle 전환|새 데이터 및 RUN 조건으로 유효성 표시 PASS|
|Close / timeout / 재연결|이전 입력 유효성 제거·새 입력 요구 PASS|
|임의 Result / Done 또는 입력 에코|수신한 모든 produced payload에서 발생 없음|

NATIVE_PROBE.json에는 총24개 검사와 응답 바이트·snapshot·sequence가 있다.
sequence 수는 합성 패킷 수이며 실제 제품 검사 횟수나 현장 신뢰성 수치가 아니다.
timeout 관찰 루프 시간은 약 0.167s다. 정밀한 PLC 지연 측정이 아니다.

검증 중 발견·수정한 문제:

1. 첫 후보는 연결마다 Run/Idle 진단을 0으로 지웠다. upstream은 동일 RUN 값으로 재연결되면
   RunIdleChanged를 호출하지 않아, 새 데이터가 와도 IDLE로 남았다.
   최종 후보는 upstream header 캐시의 mirror를 유지하고, 연결 및 해당 연결의 새 수신 여부로 유효성을 제한한다.
   Close/timeout 뒤 이전 데이터만으로 controls_valid가 되는 동작은 허용하지 않는다.
2. 최초 격리 환경의 loopback에는 multicast 설정이 없어 수신 검사가 실패했다.
   host 네트워크에 접근하지 않고 private namespace 안에만 multicast 지원을 설정했다.
3. timeout 뒤 upstream은 TCP encapsulation session도 닫는다.
   이를 무시하지 않고 EOF·프로세스 생존·새 RegisterSession·새 Forward Open을 순서대로 검증했다.

NATIVE_PROBE_ATTEMPT1/2/3.json은 실패한 과정도 보존한다. 성공 결과로 덮어쓰지 않았다.
controls_valid는 통신/인코딩 진단 값이며 설비 운전 허가나 안전 인터록 판정이 아니다.
upstream의 변환·미사용 변수 등 compiler warning 86줄은 BUILD_WARNINGS.json에 남겼다.
수정한 sampleapplication.c의 warning은 0이며 upstream 전체 정리·보안 인증은 이 작업 범위가 아니다.

## 5. 실제 PLC 추가 검증

- 실제 온라인 태그 순서, 각 BOOL의 2B 점유·bit 위치·endianness와 ON/OFF 바이트.
- 실제 EDS import/Identity keying/Connection parameter, 구성 데이터와 Forward Open 응답.
- 현장 NIC enP8p1s0, 스위치 multicast 전달, 실제 50ms cyclic traffic와 timeout.
- Result와 Done 각각의 매핑 및 실제 PLC 결과 소비. 읽기 성공을 소비 ACK로 취급하지 않는다.
- Python bridge가 없으므로 현재 후보는 실제 검사 완료나 PASS/FAIL을 발행하지 못한다.

## 6. 현장 적용 전 승인

다음 별도 Task에서 설치·서비스 전환·현장 I/O 활성화 범위와 실제 설비 정지 상태를 확인해야 한다.
기존 Explicit 결과 발행자와 새 cyclic bridge의 단일 쓰기 주체를 먼저 정하고, 중복 발행을 차단해야 한다.
실제 PLC/Sysmac 변경이 필요해지면 정확한 변경안을 제시한 후 별도 승인한다.
이번 작업은 그 적용·승인·기동을 실행하지 않았다.

## 7. 보존·롤백

183개 후보/증거 파일 회수 후 각 SHA256 검증 PASS; 생성 원본과 회수 profile 168개 파일도 일치했다.
ISOLATED_CANDIDATE.tar.gz SHA256: de135a52193ac9704616d45a69d03173b2a78f9e4469d2e738b0712a7f79cb5a
PC 패키지에는 C 소스·EDS·PROFILE·실제 ARM64 binary·빌드/검증 증거가 포함된다.

운영 설치본 manifest 4개 파일 및 runtime/config 해시는 전후 동일하다.
engine-inspector.service MainPID1078 / NRestarts0 / active / enabled 유지.
현장 host에서 OpENer TCP44818/UDP2222 listener는 없고, 기존 Python의 PLC explicit 연결만 유지됐다.
이번에 만든 remote scratch 하나는 노트북 해시 확인 및 의존 프로세스 없음 확인 후 삭제했다.
다른 후보·운영 파일·환경·시스템 로그는 정리하지 않았다.

운영본을 바꾸지 않았으므로 현재 장치에 수행할 롤백은 없다.
후보를 취소하려면 노트북의 이 격리 후보를 미채택으로 남기면 된다.
향후 배포 시에는 당시 운영본의 검증된 백업과 별도 복원 절차가 필요하다.

## 8. 종료·남은 문제

이번 Task는 **완료·STOP**이다. 실제 PLC 통신은 미검증이며 설치본은 아직 2B 분리 계약 상태다.
Python 검사 bridge, 기존 runtime TypeError, 카메라/AI/제품 반복 검증은 수행하지 않았다.
후속 Task는 명시 승인 이후 실제 wire 계약 검증, bridge 구현과 단일 결과 발행자 전환이다.
현재 후보를 정식 runtime 또는 현장 통신 PASS로 표시하지 않는다.

근거: UNIT_TEST_RESULT.json, native_verified/NATIVE_PROBE.json, native_verified/BUILD.json,
RETRIEVAL_VERIFICATION.json, PRESERVATION_VERIFICATION.json, CLEANUP.json, HOST_BEFORE/AFTER.json.
