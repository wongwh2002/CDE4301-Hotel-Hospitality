# Face worker model

The POC uses InsightFace's **`buffalo_l`** package through `FaceAnalysis` and ONNX Runtime. Docker Compose selects `CPUExecutionProvider` by default. On an Apple Silicon Mac, the opt-in native worker can select Core ML and keep CPU fallback enabled:

- `FACE_EXECUTION_PROVIDER=cpu` explicitly selects CPU (the default, including Docker).
- `FACE_EXECUTION_PROVIDER=coreml` selects Core ML with `CPUAndGPU` compute units and ONNX Runtime CPU fallback. It fails at startup if Core ML is unavailable. On the tested M1, this assigned all profiled `buffalo_l` operations to the Core ML GPU; `CPUAndNeuralEngine` assigned them to Core ML CPU.
- `FACE_EXECUTION_PROVIDER=auto` leaves provider selection to InsightFace / ONNX Runtime.
- `COREML_COMPUTE_UNITS` supports `CPUOnly`, `CPUAndNeuralEngine`, `CPUAndGPU`, or `ALL`.
- `COREML_PROFILE_COMPUTE_PLAN=true` asks ONNX Runtime to log the per-operation hardware compute plan. Check those logs to verify Neural Engine/GPU placement; the session's available provider list alone does not prove where each operation ran.

The face-worker `/health` response reports its requested provider mode, available providers, provider list for every loaded model session, Core ML compute units/profile setting, model initialization duration, and active match thresholds. The native setup and paired benchmark workflow are documented in the repository [README](../../README.md#optional-run-the-face-worker-natively-on-an-m1-mac). Native macOS/Core ML inference runs outside Docker; lounge-control and mock-hotel can remain in Compose through `compose.m1-native.yaml`.

The active models are:

- **SCRFD-10GF** detects faces and five-point landmarks.
- **ResNet-50 / ArcFace** creates a normalized 512-value face embedding.

The package includes other analysis models, but the worker enables only `detection` and `recognition`. Model weights are downloaded on first startup into the Compose `face-model-cache` volume, under `/models/insightface/models/buffalo_l`; they are not stored in Git or the mock-hotel database. The volume must have enough disk space and the first startup needs network access. The InsightFace model table reports 326 MB for the full package and 97.25 IJB-C (E4), 99.33 CFP-FP, and 98.23 AgeDB-30 for `buffalo_l`. These are upstream benchmark figures, not expected POC accuracy. [InsightFace model zoo](https://github.com/deepinsight/insightface/blob/master/python-package/docs/model_zoo.md)

Matching uses a provisional `0.65` cosine threshold, a `0.10` margin over the next candidate, and confirms a candidate that passes in at least two of the latest three observations. The threshold is an initial POC setting based on the official example, not a locally validated operating point; tune it against the lounge's open-set matching task before interpreting cues. The worker stores normalized embeddings for active candidates in RAM; frames and reference photos are discarded after inference. Seeded Alex has a fictional generated face for frame replay; other seeded profiles use a person-free JPEG and cannot be enrolled for face matching. The replay checks pipeline wiring with the same synthetic image, not recognition accuracy or generalization. [InsightFace face-recognition example](https://github.com/deepinsight/insightface/blob/master/examples/face_recognition/insightface_app.py)
