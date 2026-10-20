# 문서 버전과 기존 참조 대응

승인 PDF·README 본문과 해시를 보존했다. 아래 표는 과거 참조의 해석을 돕는 외부 안내이며 원문을 변경하지 않는다.

| ID | 최신 제출 문서 | 버전 |
|---|---|
| 01 | [문제정의서](01_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_%EB%AC%B8%EC%A0%9C%EC%A0%95%EC%9D%98%EC%84%9C_v1.1.pdf) | 1.1 |
| 02 | [데이터셋 설명서](02_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%85%8B_%EC%84%A4%EB%AA%85%EC%84%9C_v1.2.pdf) | 1.2 |
| 03 | [모델 평가서](03_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_%EB%AA%A8%EB%8D%B8_%ED%8F%89%EA%B0%80%EC%84%9C_v1.1.pdf) | 1.1 |
| 04 | [최적화 전후 Benchmark](04_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_%EC%B5%9C%EC%A0%81%ED%99%94%EC%A0%84%ED%9B%84_Benchmark_%EB%B3%B4%EA%B3%A0%EC%84%9C_v1.2.pdf) | 1.2 |
| 05 | [통합 테스트 결과서](05_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_%ED%86%B5%ED%95%A9%ED%85%8C%EC%8A%A4%ED%8A%B8_%EA%B2%B0%EA%B3%BC%EC%84%9C_v1.0.pdf) | 1.0 |
| 06 | [DB 구조·조회 방식](06_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_DB_%EA%B5%AC%EC%A1%B0%EC%99%80_%EC%A1%B0%ED%9A%8C%EB%B0%A9%EC%8B%9D_v1.0.pdf) | 1.0 |
| 07 | [Jetson 실행·변환 절차서](07_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_Jetson_%EC%8B%A4%ED%96%89_ONNX_TensorRT_%EC%A0%88%EC%B0%A8%EC%84%9C_v1.1.pdf) | 1.1 |
| 08 | [프로젝트 기획안](08_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8_%EA%B8%B0%ED%9A%8D%EC%95%88_v1.1.pdf) | 1.1 |
| 09 | [코드 저장소 README](09_project_readme_v1_1.md) | 1.1 |
| 10 | [최종 결과보고서](10_final_report_v1_2.pdf) | 1.2 |
| 11 | [데이터셋 구축 프로그램 설명서](11_dataset_program_manual_v1_0.pdf) | 1.0 |

## 과거 참조 대응

| 원문에 남아 있는 참조 | 현재 제출본 | 처리 |
|---|---|
| 01 v1.1 → 04 v1.1 / 07 v1.0 | 04 v1.2 / 07 v1.1 | 옛 PDF 경로 유지 |
| 03 v1.1 → Benchmark v1.1 | 04 v1.2 | 원본 Benchmark evidence v001 동일 |
| 07 v1.1 → 04 v1.1 및 고정 보고서 커밋 | 04 v1.2 | 고정 링크와 과거 파일 유지 |
| 08 v1.1 → 04 v1.1 / 09 v1.0 / 10 v1.1 | 04 v1.2 / 09 v1.1 / 10 v1.2 | 본문은 작성 당시 참조로 보존 |

## 링크 호환용 과거 PDF

- [07_엔진모형_Jetson_실행_ONNX_TensorRT_절차서_v1.0.pdf](07_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_Jetson_%EC%8B%A4%ED%96%89_ONNX_TensorRT_%EC%A0%88%EC%B0%A8%EC%84%9C_v1.0.pdf) — 원래 파일·바이트 유지, 최신 제출 표에서 제외.
- [04_엔진모형_최적화전후_Benchmark_보고서_v1.1.pdf](04_%EC%97%94%EC%A7%84%EB%AA%A8%ED%98%95_%EC%B5%9C%EC%A0%81%ED%99%94%EC%A0%84%ED%9B%84_Benchmark_%EB%B3%B4%EA%B3%A0%EC%84%9C_v1.1.pdf) — 원래 파일·바이트 유지, 최신 제출 표에서 제외.

## 원본과 검토 기록

데이터셋 v002, 모델 평가 v001, Benchmark v001, 통합시험 v001은 문서 개정과 독립된 원본 식별자다. 최신 문서와 함께 그대로 제공한다.
과거 audit/manifest의 날짜·입력 이름·해시는 원래 검토 범위를 유지한다. `document_audits/old10/`은 10 v1.1 당시 기록이며 최신 v1.2 검증이 아니다.
코드 README는 09 v1.1과 동일해 ALREADY_APPLIED다. `cfaa372...` 평가 코드, `bdadacc...` README 반영 커밋, `4c4b...` 시험본, `32c4...` 후속 UI 운영본의 의미를 혼동하지 않는다.
R0/P0 초기 계획 원문 출처 미확인은 [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md)의 한계에 기록했다.
