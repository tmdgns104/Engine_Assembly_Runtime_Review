# A. 현재 운영 상태

근거: [서비스 관측](../manifests/SERVICE_OBSERVATION.json), [API 두 시점 관측](../manifests/RUNTIME_OBSERVATIONS.json), [Release API](../manifests/RELEASE_API.json), [배포 manifest](../manifests/DEPLOYED_RELEASE.json).

|항목|실제 확인|수준|
|---|---|---|
|서비스|engine-inspector.service enabled / active / running, MainPID 1082, NRestarts 0|VERIFIED_RUNTIME|
|실행 명령|`/home/jetson/oned_device_bench/envs/app_v1/bin/python -B -X utf8 /home/jetson/oned_device_bench/current/standalone_service.py --config /home/jetson/oned_device_bench/config/standalone.json`|VERIFIED_RUNTIME|
|Python|venv app_v1의 실행 경로, /proc/exe는 /usr/bin/python3.10|VERIFIED_RUNTIME|
|소스|`/home/jetson/oned_device_bench/current`; 현재 경로는 symlink 아님|VERIFIED_RUNTIME|
|Release|engine-dev-28d6e107b0f2a6c3 / DEVELOPMENT_BASELINE_NOT_PRODUCTION_ACCEPTED|VERIFIED_RUNTIME|
|Web|0.0.0.0:18771, PID1082|VERIFIED_RUNTIME|
|카메라|ready=true, 1280×720 BGR8, 서로 다른 frame/sequence/PTS로 갱신|VERIFIED_RUNTIME|
|검사 worker|PID2790 alive, 서비스 IDLE/ready=true, 실제 전체 검사 active ID 없음|VERIFIED_RUNTIME|
|분류기|AssemblyInspector ready=true / REQUIRED_FINAL_COMPONENT / 대기|VERIFIED_RUNTIME: 로딩 상태; 판정 정확도 시험 아님|
|상위 runtime|loop_alive=true, operating=false, phase=FAULT, TypeError|FAILED|
|PLC|192.168.50.2→192.168.50.3:44818 TCP established, backend OMRON_CIP_BENCH, available=true|VERIFIED_RUNTIME: Explicit 읽기 경로|
|실제 결과 쓰기|legacy_publication_enabled=false, runtime network_plc_writes_enabled=false|VERIFIED_RUNTIME|
|PLC 상태|LEGACY_THREE_BOOL / RESYNC_REQUIRED / BLOCKED / Request=false|FAILED|
|OpENer|현장 TCP44818/UDP2222 listener·OpENer 프로세스 없음|VERIFIED_RUNTIME|
|전체 사이클|요청→현재 검사→PLC 소비→배출 반복|NOT_VERIFIED / 현재 차단|

서비스 active는 검사 준비 완료를 뜻하지 않는다. 하위 InspectionService는 카메라와 모델 관점에서 ready지만 상위 StandaloneRuntime은 오류로 운전 중이 아니다. 현재 preview는 `TRACKING_ONLY_PARTS_NOT_EVALUATED`이며 저장된 PASS/FAIL이 아니다.

`integrated_counts`는 PASS/FAIL/REVIEW/ERROR 모두 0이고 이번 세션 history도 비어 있다. 이는 전체 과거 DB에 아무 검사도 없다는 뜻이 아니다. 유지보수 화면은 별도의 과거 부품 검사 기록을 보여준다. 원본 DB/검사 이력은 공유하지 않았다.

## 실행 구성과 한계

[서비스 단위](../config_reference/engine-inspector.service.txt)는 Type=simple, Restart=on-failure, RestartSec=10, start limit 300초/5회, KillMode=control-group이다. Python 루프가 예외를 잡고 계속 살아 있는 지금 상태에서는 systemd active가 유지되며 Restart 정책이 이 논리 오류를 자동 복구하지 않는다.

네트워크 경로는 `enP8p1s0`의 현장망이며 노트북/Tailscale을 PLC 통신 중계로 쓰는 경로는 관측되지 않았다. 노트북 OFF·인터넷 단절·실제 재부팅 시험은 이번에 하지 않았다. 새 boot ID가 관측됐지만 이를 이번 작업의 재부팅 성공 시험으로 세지 않는다. systemd와 ps의 시작 시각 표현에 차이가 있어 부팅 소요시간/통신 지연을 계산하지 않았다.

현장 URL: `http://192.168.50.2:18771/auto`, `/line`, `/`. 이번 브라우저는 기존 원격 주소 `http://100.119.148.89:18771`로 조회했다. IP 접속 가능과 작업장 안전/AI 정확도/결과 소비는 별개다.

현장 벨트가 실제 정지했는지, 버튼·비상정지의 안전 기능이 동작하는지는 이번 조사에서 시험하지 않았다.

종료 전 16:20 KST 읽기 전용 재확인에서도 MainPID1082/NRestarts0/동일 boot·session, FAULT/RESYNC_REQUIRED/BLOCKED, writes=false를 확인했다. PID2790이 `/dev/video0`을 소유하며 frame sequence24838까지 갱신됐다. 선택 파일125개가 초기 해시와 같았다. [보존 근거](../manifests/FINAL_PRESERVATION.json).
