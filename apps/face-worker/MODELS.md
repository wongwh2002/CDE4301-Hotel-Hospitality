# Face worker model baseline

The first local CPU baseline uses OpenCV DNN through `opencv-contrib-python-headless`:

- **YuNet** detects and aligns faces: `face_detection_yunet_2023mar.onnx`.
- **SFace** derives a 128-element face embedding: `face_recognition_sface_2021dec.onnx`.

Model bytes are downloaded on first startup into the Compose `face-model-cache` volume and checked against pinned SHA-256 digests. They are not stored in Git, the mock-hotel database, or the frame queue. OpenCV Zoo lists separate licenses for its models; preserve the model-specific license notice if distributing them. See the [YuNet model folder](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet) and [SFace model folder](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface).

The current matching settings (`0.50` cosine score, `0.10` best-versus-next margin, and three stable frames) are initial engineering guardrails, not validated operating thresholds. The worker stores only normalized embeddings for active candidates in RAM; frames and reference photos are discarded after inference. Seeded Alex has a fictional generated face for the local frame-replay smoke demo; the other seeded profiles use a person-free JPEG and cannot be enrolled for face matching. This fixture checks only that one reference matches its identical replay image, not recognition accuracy or generalization.

The SFace folder's Apache-2.0 notice covers the model files, but the model's training-data provenance has an open question in the [OpenCV Zoo issue tracker](https://github.com/opencv/opencv_zoo/issues/313). Treat it as a development baseline; review provenance and intended-use terms before deploying beyond this local POC.
