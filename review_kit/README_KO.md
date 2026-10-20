# DB 조회 검토 자료 — 7건 발췌 파생본

이 폴더는 기존 통합시험 증빙을 평가자가 장치 없이 조회할 수 있도록 만든 자료입니다.
새 검사, 가상 검사, 임의의 성공 행을 추가하지 않았습니다.

## 데이터의 출처와 범위

- 입력: Engine_Integrated_Test_Evidence_v001.zip의 db/schema.sql, db/selected_rows.json.
- 원본 ZIP SHA-256: c2f4b068f372cb2f9a972107e49b0862b27692f5ab7ac660ff0c1afc9aad1ace
- inspection_review_subset.sqlite3: 원래 스키마 10개 테이블과 선택된 8개 테이블의 169행을 삽입한 **검토용 파생 DB**입니다.
- inspections 7, cycles 7, defects 3, frame_assets 28, events 55, outbox 55, service_state 14, dispositions 0행.
- calibrations와 quarantine은 원문 스키마만 제공되었습니다. 발췌 DB의 빈 테이블을 실제 운영 기록 없음으로 해석하지 않습니다.
- JSON TEXT는 원래 문자열로 보존했습니다. NULL·열 이름·행 값도 원문과 대조했습니다.
- 실제 368건 운영 스냅샷의 백업본이 아니며 운영 장치에 복원하거나 덮어쓰지 마세요.
- 실물시험은 2026-10-18의 4c4b 실행본, 이력 GET 기록은 2026-10-20입니다. 원문 범위를 유지합니다.

## 읽는 순서

1. 06 DB 구조·조회 방식 설명서 PDF에서 테이블 관계와 조회 기준을 확인합니다.
2. query_results의 CSV는 별도 환경 준비 없이 열 수 있는 조회 결과입니다.
3. SQL 직접 확인은 queries_readonly.sql과 query_definitions.json을 사용합니다.
4. 자동 대조는 이 폴더에서 `python run_queries.py`를 실행합니다. 스크립트는 자신의 발췌 DB만 읽으며 경로 인자를 받지 않습니다.

Python 3와 JSON 함수를 지원하는 SQLite가 필요합니다. 추가 패키지는 사용하지 않습니다.
각 SELECT 결과를 보존 CSV와 대조하고 마지막에 DB 해시가 유지되는지 확인합니다.
운영 서비스, 카메라, PLC, 네트워크에 접근하지 않습니다. 실행 결과는 콘솔에만 출력합니다.

## 파일 설명

- schema_original.sql / selected_rows_original.json: 원본 입력의 바이트 사본.
- queries_readonly.sql: SELECT 예시 8개.
- query_definitions.json: SQL과 바인딩 매개변수.
- query_results/Q01~Q08.csv: 각 실행 결과. 표의 기본/최종 판정 및 날짜 범위를 구분합니다.
- query_results/history_export_7.csv: 원문 csv_text()를 발췌 DB의 검색 결과에 적용한 로컬 파생 CSV. 새 HTTP 내보내기 결과가 아닙니다.
- source_snapshot/src/config.py 및 src/journal/history.py: 원문 이력 읽기 코드의 사본. 실행 서비스 전체 설치본은 아닙니다.
- tables/column_dictionary.csv: 테이블 10개, 열 67개의 SQLite 선언 타입·NOT NULL·PK 순서·기본값. 기본키 자체와 NOT NULL 별도 선언은 구분합니다.
- review_verification.json: 소스 무결성·실제 사진 해시·파생본 원값·47개 로컬 조회 점검. 실제 장치 재검증과 별도입니다.

원본 사진은 함께 제공된 원본 증빙 ZIP을 압축 해제한 뒤 frame_assets.relative_path에서 찾습니다.
발췌 DB에 사진 바이트는 저장하지 않았습니다. 메타데이터와 실파일을 연결하여 확인합니다.

## 중요한 구분

- counts와 decision 필터는 기본 inspections.decision을 사용합니다. 최종 판정은 final_decision 열입니다.
- events.payload_json 안의 이전 검사 참조를 해당 검사의 직접 완료 사건으로 세지 않습니다.
- outbox와 frame_assets의 PENDING은 원값입니다. 이를 로컬 저장 실패나 PLC 송신 실패로 바꾸어 해석하지 않습니다.
- 자동 PLC 소비 확인 필드는 false 그대로 보존되어 있습니다. 실제 LED·컨베이어의 사용자 관찰은 원본 user_observations.md와 05 통합테스트 결과서에 별도로 있습니다.
