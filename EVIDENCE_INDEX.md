# 원본 증빙과 문서 근거 찾아보기

승인 문서의 근거 ID를 현재 제출 경로로 연결한다. 원본 ZIP의 바이트·내부 경로와 과거 검토 기록은 변경하지 않았다. 아래 경로는 ZIP을 내려받아 압축 해제한 뒤 찾는다. 새 추론·현장시험·모델 변환의 결과가 아니다.

## 02 데이터셋 설명서

원본: [M1_M2_dataset_evidence_v002.zip](M1_M2_dataset_evidence_v002.zip). 경로 기준: `M1_M2_dataset_evidence_v002/`.

| 근거 ID | 원본 내부 경로 |
|---|---|
| S1 | `tables/dataset_summary.csv`<br>`tables/class_box_counts.csv`<br>`tables/scenario_distribution.csv`<br>`tables/unique_originals_and_copies.csv` |
| S2 | `metadata/M1/data.yaml`<br>`metadata/M2/data.yaml` |
| S3 | `samples.csv`<br>`SAMPLES_KO.md`<br>`samples/images/`<br>`samples/labels/M1/`<br>`samples/labels/M2/` |
| S4 | `tables/all_image_label_links.csv`<br>`tables/matching_and_split_checks.csv` |
| S5 | `CAPTURE_AND_REVIEW_KO.md`<br>`provenance/capture_conditions_train_val.json` |
| S6 | `metadata/M1/annotations_used.json`<br>`metadata/M1/approval.json`<br>`metadata/M1/approval_provenance.json` |
| S7 | `metadata/M2/dataset_pose_audit_v004.json` |
| S8 | `verification/verification.json`<br>`bundle_manifest.json`<br>`provenance/copied_sources.csv` |
| S9 | `provenance/current_model_links.json` |
| S10 | `appendix/REFERENCE_CLASSIFICATION_KO.md`<br>`appendix/reference_classification_summary.json` |
| S11 | `tables/full_dataset_files.csv`<br>`provenance/FILE_RECONSTRUCTION_KO.md` |

## 03 모델 평가서

원본: [M1_M2_model_evaluation_evidence_v001.zip](M1_M2_model_evaluation_evidence_v001.zip). 경로 기준: `ZIP 루트`.

| 근거 ID | 원본 내부 경로 |
|---|---|
| S1 | `M1/training/args.yaml`<br>`M1/training/results.csv`<br>`M1/execution/train_engine_parts.py`<br>`M1/execution/training_console_utf8.log` |
| S2 | `M2/training/args.yaml`<br>`M2/training/results.csv`<br>`M2/execution/train_envelope.py`<br>`M2/execution/train_console_v004.log` |
| S3 | `shared/source_index.json`<br>`M1/dataset/`<br>`M2/dataset/` |
| S4 | `M1/validation_metrics.json`<br>`M2/training_result.json`<br>`tables/validation_metrics.csv` |
| S5 | `M1/validation/` |
| S6 | `M2/validation/` |
| S7 | `M1/review/prediction_diagnostics.json`<br>`M1/review/visual_review.json`<br>`M1/predictions/val_predictions.jsonl` |
| S8 | `M2/predictions/envelope_predictions_e03.json` |
| S9 | `examples.csv`<br>`EXAMPLES_KO.md`<br>`examples/` |
| S10 | `verification/model_hash_chain.json`<br>`M1/conversion/`<br>`M2/conversion/`<br>`M1/deployment/`<br>`M2/deployment/`<br>`runtime/` |
| S11 | `M1/parity/parts_parity_v001.json`<br>`M1/parity/reference/`<br>`verification/parity_record_audit.json` |
| S12 | `bundle_manifest.json`<br>`verification/bundle_checks.json` |

B1 → [M1_M2_benchmark_evidence_v001.zip](M1_M2_benchmark_evidence_v001.zip)의 `protocol.json`, `accuracy_summary.csv`, `accuracy_by_class.csv`, `model_hashes.json`, `remote_results/results/`의 전체 예측. S12의 ZIP 옆 검증은 과거 기록의 표현이며 현재 제출 검증은 [PACKAGING_VERIFICATION.json](PACKAGING_VERIFICATION.json)에 있다.

## 04 최적화 전후 Benchmark

원본: [M1_M2_benchmark_evidence_v001.zip](M1_M2_benchmark_evidence_v001.zip). 경로 기준: `ZIP 루트`.

| 근거 ID | 원본 내부 경로 |
|---|---|
| B01 | `README_KO.md` |
| B02 | `protocol.json` |
| B03 | `environment.json`<br>`environment_effective.json`<br>`telemetry_raw.jsonl`<br>`telemetry_summary.json` |
| B04 | `input_manifest.csv`<br>`ground_truth.json`<br>`ground_truth/M1/`<br>`ground_truth/M2/` |
| B05 | `latency_raw.csv`<br>`latency_summary.csv`<br>`remote_results/results/` |
| B06 | `memory_raw.csv`<br>`memory_summary.csv`<br>`remote_results/results/` |
| B07 | `accuracy_summary.csv`<br>`accuracy_by_class.csv`<br>`remote_results/results/` |
| B08 | `provenance/M1/`<br>`provenance/M2/`<br>`model_hashes.json`<br>`model_hash_verification.json` |
| B09 | `attempt001/`<br>`first_suite_failure.json`<br>`protocol_revisions/`<br>`low_cutoff_native_rejections.json` |
| B10 | `examples.csv`<br>`examples/`<br>`prediction_comparison.csv` |
| B11 | `remote_results/window_result.json`<br>`restore_observation_174722.json`<br>`operating_after_verification.json` |
| B12 | `code/`<br>`source_snapshot/`<br>`adapter_tests.json`<br>`collected_evidence_verification.json`<br>`verification.json`<br>`bundle_manifest.json` |

B13 → [document_audits/04/reviewer_audit.json](document_audits/04/reviewer_audit.json). 당시 문서 검토 기록이며 현재 v1.2 PDF의 새 검증으로 바꾸지 않았다.

## 05 통합 테스트 결과서

원본: [Engine_Integrated_Test_Evidence_v001.zip](Engine_Integrated_Test_Evidence_v001.zip). 경로 기준: `ZIP 루트`.

| 근거 ID | 원본 내부 경로 |
|---|---|
| E01 | `sources/field_ten/`<br>`trial_reconciliation.json` |
| E02 | `assets/`<br>`asset_manifest.csv` |
| E03 | `inspection_results.csv`<br>`assets/` |
| E04 | `db/selected_rows.json`<br>`db/per_inspection/`<br>`db/schema.sql`<br>`db/event_links.json` |
| E05 | `queries/`<br>`remote_recovery_receipt.json` |
| E06 | `sources/screens/UI_CROP_JETSON.png`<br>`sources/screens/UI_CROP_JETSON.json` |
| E07 | `user_observations.md` |
| E08 | `PLC_LINKAGE_KO.md`<br>`sources/plc/` |
| E09 | `TIME_AND_FIELD_MAP_KO.md`<br>`timing_summary.csv` |
| E10 | `release_linkage.json`<br>`release_file_changes.csv`<br>`sources/transition/`<br>`sources/ui_transition/` |
| E11 | `bundle_manifest.json`<br>`verification.json`<br>`code/`<br>`logs/` |
| E13 | `appendix/`<br>`missing_evidence.md` |

E12 → [document_audits/05/reviewer_audit.json](document_audits/05/reviewer_audit.json), [document_audits/05/timing_recomputed.csv](document_audits/05/timing_recomputed.csv), [document_audits/05/figure_provenance.json](document_audits/05/figure_provenance.json). 과거 84항목 검증을 이번에 다시 수행한 것으로 주장하지 않는다. `assets/<inspection_id>/`에서 같은 ID의 원본·결과·통합 결과를 찾는다.

E10의 문서상 `ui_transition/` 축약 경로는 실제 ZIP의 `sources/ui_transition/`에 대응한다. 위 표는 실제 경로이며 승인 PDF의 본문은 수정하지 않았다.

## 06 DB 구조·조회 방식

원본: [Engine_Integrated_Test_Evidence_v001.zip](Engine_Integrated_Test_Evidence_v001.zip). 경로 기준: `ZIP 루트`.

| 근거 ID | 원본 내부 경로 |
|---|---|
| D01 | `README_KO.md`<br>`DB_AND_QUERY_KO.md` |
| D02 | `db/schema.sql`<br>`db/selected_rows.json`<br>`db/export_verification.json` |
| D03 | `db/per_inspection/`<br>`assets/` |
| D04 | `sources/tested_runtime/src/journal/history.py`<br>`sources/tested_runtime/src/config.py`<br>`sources/tested_runtime/apps/edge_service/history_api.py` |
| D05 | `sources/tested_runtime/src/runtime/standalone.py`<br>`sources/tested_runtime/src/runtime/standalone_web.py` |
| D06 | `asset_manifest.csv`<br>`assets/`<br>`queries/` |
| D07 | `db/selected_rows.json`<br>`db/event_links.json`<br>`db/queries.sql` |
| D08 | `db/source_snapshot_receipt.json`<br>`sources/historical_snapshot_post7.py` |
| D09 | `sources/screens/UI_CROP_JETSON.png`<br>`release_linkage.json`<br>`release_file_changes.csv` |

D10 → [review_kit/README_KO.md](review_kit/README_KO.md)와 [review_kit/inspection_review_subset.sqlite3](review_kit/inspection_review_subset.sqlite3); [review_kit/query_definitions.json](review_kit/query_definitions.json)의 SELECT 8개, [review_kit/query_results/](review_kit/query_results/)의 예상 CSV, [review_kit/run_queries.py](review_kit/run_queries.py)의 읽기 전용 재조회 코드. D02의 축약 파일명은 모두 원본 `db/` 아래이며, D03의 `integrated_final.json`은 각 `assets/<inspection_id>/` 아래다.

## 07 실행·변환 출처

평가 코드 고정 커밋: [cfaa372eece0cd6a7dc659cc316c256fb4b6af76](https://github.com/tmdgns104/Engine_Assembly_Defect_Inspector/tree/cfaa372eece0cd6a7dc659cc316c256fb4b6af76). 현재 업로드 커밋이나 장치 release ID와 구분한다.

G1~G9의 실제 코드 링크는 승인된 07 PDF 부록 A에 있다. [07_Jetson_실행코드_근거맵.md](07_Jetson_%EC%8B%A4%ED%96%89%EC%BD%94%EB%93%9C_%EA%B7%BC%EA%B1%B0%EB%A7%B5.md)도 이전 안내의 고유 출처를 보존했다. 실행 안내는 최신 07 v1.1을 우선한다.

M1 `jetson/products/ENGINE_Z3005_5/dynamic_parts_005/manifest.json`, M2 `jetson/products/ENGINE_Z3005_5/envelope_v007_fp16/manifest.json`을 고정 커밋에서 확인한다. 변환 provenance는 모델 평가 ZIP의 `M1/conversion/`, `M2/conversion/` 및 Benchmark ZIP의 `provenance/M1/`, `provenance/M2/`이다.

## 과거 외부 제출 ZIP의 새 경로

| 과거 포장 | 현재 위치 |
|---|---|
| 01_problem_definition_v1_1.zip | 최신 01 개별 문서 + `document_audits/01/` |
| 04_Benchmark_제출묶음_v1.0.zip | Benchmark 원본 ZIP + `document_audits/04/` |
| 05_통합테스트_제출묶음_v1.0.zip | 통합시험 원본 ZIP + `document_audits/05/` |
| 06_DB_구조조회_제출묶음_v1.0.zip | 같은 통합시험 원본 ZIP 1개 + `review_kit/` + `document_audits/06/` |
| engine_final_report_v1_1.zip | 최신 10 v1.2 개별 문서; 과거 검증·manifest는 `document_audits/old10/` |
| 01_08_문제정의_프로젝트기획_제출묶음_v1.0.zip | 최신 01·08 v1.1; 이전 안내·manifest는 `document_audits/old01_08/` |

## 보존 범위와 확인 한계

실패·중단·attempt001, 초안·승인 기록, 빈 라벨, REVIEW·ERROR·PENDING, 과거 verification은 원문 그대로다. 원본 증빙을 보고서의 최신 버전에 맞춰 재압축하거나 숫자를 수정하지 않았다.

01의 R0와 08의 P0에 인용된 `프로젝트계획서_팀_이승훈_최신화_사람중심.md` 원문은 현재 입력 폴더와 평가 코드 고정 트리에서 확인하지 못했다. 해당 과거 출처를 새로 만들지 않았으며, 최신 08 기획안으로 원문을 대체했다고 주장하지 않는다.
