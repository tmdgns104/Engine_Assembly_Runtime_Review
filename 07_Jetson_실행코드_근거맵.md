# Jetson 실행 코드·ONNX/TensorRT 근거 맵

기준 저장소: `tmdgns104/Engine_Assembly_Defect_Inspector`
기준 브랜치: `master`
확인 커밋: `cfaa372eece0cd6a7dc659cc316c256fb4b6af76`
운영 release: `engine-integrated-32c484ac6aeb07f1`

## 실행 코드
- `jetson/standalone_service.py` — systemd foreground entrypoint, 설정/PLC 계약/lock/runtime/web 구성
- `jetson/src/vision/detector_factory.py` — manifest 기반 backend 명시 선택, silent fallback 금지
- `jetson/src/vision/engine_inspector.py` — M2 envelope → pose → rectification → M1 parts → slot decision
- `jetson/src/vision/tensorrt_native.py` — TensorRT I/O 검증, CUDA buffer/stream, execute_async_v3
- `jetson/src/vision/tensorrt_preprocess.py` — 640 letterbox, RGB, /255, contiguous batch1
- `jetson/src/vision/tensorrt_postprocess.py` — output contract, confidence, class-aware NMS, 좌표 복원
- `jetson/INTEGRATED_RUNTIME.md` — 현재 런타임 구성과 운영 범위
- `jetson/INSTALL_OPERATING_KO.md` — 다른 Orin Nano 설치·검증 절차

## 운영 모델
### M1 parts
- package: `jetson/products/ENGINE_Z3005_5/dynamic_parts_005`
- PT SHA-256: `42db183006ad2a4f61dc9c22e7a61a5b506cdacb5099004fc7c3b73b74bf5259`
- ONNX SHA-256: `433b16fd1e802bdf2cb0afba6bb6487a839d94b5adc286185b93fd3953b9c296`
- TRT SHA-256: `743ce54b4d5c7b8a36addf3dbff50fa693ec4a509b31b476f68efc69f1bf2d6c`

### M2 envelope
- package: `jetson/products/ENGINE_Z3005_5/envelope_v007_fp16`
- PT SHA-256: `cf117defe782e1ae8b355e0ed13c014fc6f1538aa2dcdbe0fb6cfa54200f7755`
- ONNX SHA-256: `5cb024bb911f9357e46c12c3d2a7e4b5f19af20e5692013037c9235e0deca830`
- TRT SHA-256: `c82f2658ac20d06985a647c15e551c681e394451cfa1c53baed64f639bcebf83`

## 변환 기록 요약
- PT → ONNX: Ultralytics YOLO.export 8.4.146, imgsz640, batch1, dynamic=False, half=False, nms=False, simplify=False, opset12
- ONNX → TensorRT: TensorRT 10.3 Builder API, workspace1GiB, optimization_level3, max_aux_streams0, TF32=False, precision_constraints=OBEY
- M1: FP16 + head FP32
- M2: FP16 + backbone FP32
- TensorRT input/output는 기록상 float32

## 함께 제출할 근거
- `03_엔진모형_모델_평가서_v1.1.pdf`
- `04_엔진모형_최적화전후_Benchmark_보고서_v1.1.pdf`
- `M1_M2_benchmark_evidence_v001.zip`
- `05_엔진모형_통합테스트_결과서_v1.0.pdf`
- `06_엔진모형_DB_구조와_조회방식_v1.0.pdf`

이 근거맵은 코드·문서 탐색용이며 새 Jetson 배포나 실물시험을 수행한 기록이 아니다.
