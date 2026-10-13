# PLC 기준본 재확인 — 푸셔없는버전 3

**새 파일에서 이송 타이머 T#2.7s와 PLC IP 192.168.50.3을 직접 확인했다.**

원본: `D:/머신러닝_학습자료/비전검사 푸셔없는버전 3 .smc2`

SHA-256: `9f491ee447dd5736858d07d2174a033a1654501b18f4c53fa641b4bf29b97806`

## 비교 결과

- 래더 23개: 변경은 rung index20 Move_Timer PT `T#1s → T#2.7s` 한 항목이다.
- IP: `192.168.250.1 → 192.168.50.3`. Subnet은 255.255.255.0이다.
- 네트워크 설정에는 IP 외 호스트 주소표/라우터표/FINS 주소표 항목 수 0→1, FINS node 1→3 변화도 있다. 전체 5개 leaf 차이를 COMPARISON.json에 기록했다. 표 개수 변화가 유효한 경로나 cyclic 연결이 있다는 뜻은 아니다.
- 전역 BOOL18개/통신 공개6개, 프로그램 변수, 물리 I/O 매핑, 내장 I/O 설정과 Program0 주기 호출 내용은 앞선 파일과 동일하다.
- 프로젝트 모델 NX1P2-9024DT1, 설정 버전1.14. 온라인 CPU 펌웨어 검증은 별도다.

## 현재 사용할 흐름

포토센서 감지 → Move_pending 유지 → 2.7초 이송 → Inspecting SET/컨베이어 운전 출력 OFF → Inspection_Request 유지 → Jetson 결과·완료 → PLC 정상/불량 기억 → 검사 해제/다음 제품 준비.

2.7초는 저장 설정을 확인한 값이며 실제 카메라 위치와 물리 정지 적합성은 미검증이다. 완료 후 Mc_Run이 유지되면 PASS/FAIL 모두 컨베이어 출력 조건이 다시 성립한다. STOP 중 Move_pending 잔여, 검사 timeout, REVIEW/ERROR 처리와 공통 배출 조건은 직전 검토에서 남은 사항이다. 이번에 래더를 바꾸지 않았다.

## 기존 신호로 통신 전환

PLC→Jetson: Mc_Run, Stop_PB, EStop_OK, Inspection_Request (BOOL Output 공개).

Jetson→PLC: Jetson_Result, Jetson_Done (BOOL Input 공개). Result=False 정상/True 불량.

앞으로 이 버전3를 PLC 구조 기준으로 사용한다. 파일명 버전3는 과거 STANDALONE_V3 통신 계약 재채택을 뜻하지 않는다. 최종 선택 방식은 EtherNet/IP cyclic I/O / Tag Data Link다. Adapter/EDS/실제 cyclic 연결은 아직 미완료다.

## 검증과 보존

원본 ZIP CRC PASS, 참고 사본 SHA 일치, 래더/변수/I/O/태스크/네트워크 비교 PASS. 원본과 이전 버전2 evidence를 보존했다. Sysmac compile, 온라인 전체 비교, 다운로드, EDS import, 실제 cyclic 교환은 NOT_RUN이다. PLC 쓰기·서비스 변경·모터 명령은 0회다.
