# JPEG XL for the lounge POC image path

**Checked:** 2026-10-16
**Scope:** Whether `.jxl` should replace JPEG for guest reference photos, phone-to-`lounge-control` frames, and face crops in the current local Docker POC.

## Recommendation

Keep **JPEG as the current wire and CV format** for guest photos, frames, and face crops. Do not convert the Weng or PH JPG fixtures to JXL for the recognition run. JPEG XL is now a credible browser display format: Safari supports it from Safari 17, Chrome is shipping decoding from Chrome 155, and Firefox 158 enables it by default. That browser progress does not yet remove the work in this project’s frame protocol, server validation, and exact OpenCV decoder build. The browser `toBlob()` path in the dashboard also needs an encoder, while Chrome's announced support is decoding support.

Treat JXL as an optional **measured transport experiment** later if frame bandwidth is a real bottleneck. Compare it on representative captures for bytes per frame, encode/decode latency, and recognition results before changing the protocol. Keep the original JPG fixtures intact as the reproducible baseline.

## How this repo handles images today

- The device-stream contract fixes frame `format` to `image/jpeg`; the Python message model has the same literal value. The WebSocket forwards those bytes to the face worker. ([device-stream schema](../../contracts/device-stream.schema.json), [contract models](../../contracts/models.py), [lounge-control frame path](../../apps/lounge-control/main.py))
- The face-worker HTTP frame endpoint returns `415` unless `Content-Type` is `image/jpeg`. Its decoder calls `cv2.imdecode()` and reports a JPEG decode error. Face crops are encoded as `.jpg`, and the crop contract's MIME type is `image/jpeg`. ([face-worker ingress](../../apps/face-worker/main.py), [vision decoder and crop encoder](../../apps/face-worker/vision.py), [face-crop schema](../../contracts/face-crop.schema.json))
- The dashboard file input lists JPEG, PNG, and WebP, then its camera/frame path uses `canvas.toBlob(..., 'image/jpeg', 0.82)`. It sends a `frame_meta` format of `image/jpeg`. ([dashboard input and encoder](../../apps/lounge-control/dashboard.py))
- The face-worker pins `opencv-python-headless==4.14.0.94` but does not declare a JPEG XL decoder package. OpenCV's current API documentation exposes JPEG XL encoding options; that alone does not demonstrate that this specific prebuilt wheel can decode JXL. The OpenCV Python wheel project says a custom build may be needed when a dependency is not enabled in its prebuilt wheel. ([face-worker requirements](../../apps/face-worker/requirements.txt), [OpenCV image-codec flags](https://docs.opencv.org/doc/doxygen/html/d8/d6a/group__imgcodecs__flags.html), [opencv-python build and wheel notes](https://github.com/opencv/opencv-python#manual-builds))

## Format and client compatibility

JPEG XL is standardized as ISO/IEC 18181 and supports lossy and lossless coding. The reference implementation documents lossless transcoding of JPEGs so the original JPEG can be reconstructed. This is useful for archival or storage workflows, but it does not by itself make this POC's live pipeline faster: frames still need decoding to pixels for CV inference. ([libjxl overview and usage](https://github.com/libjxl/libjxl))

Browser decoder support has improved recently:

| Client | Status at check date | What it means here |
| --- | --- | --- |
| Safari | Apple lists JPEG XL support starting in Safari 17. | A browser may display JXL, but the companion phone and Docker CV decoder still need independent support. |
| Chrome | Chrome announced built-in JPEG XL **decoding** starting with Chrome 155. | This is decode support, not an announced browser Canvas encoder for the dashboard's outgoing frames. |
| Firefox | Firefox 158 stable, released 2026-10-13, enabled `image/jxl` by default. | Recent Firefox clients can decode JXL; older releases and other embedded WebViews may differ. |

Sources: [Safari 17 release notes](https://developer.apple.com/documentation/safari-release-notes/safari-17-release-notes), [Chrome: Shipping JPEG XL in Chrome](https://developer.chrome.com/blog/jpeg-xl-in-chrome), [Firefox 158 release notes](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/158).

The Canvas `toBlob()` API emits the requested format only if that user agent supports that encoder; otherwise it falls back to PNG. The current dashboard explicitly asks for JPEG. Do not infer JXL **encoding** support from a browser's ability to decode JXL. ([MDN `HTMLCanvasElement.toBlob()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/toBlob))

## What adopting JXL would require

Sending JXL bytes through the existing raw binary WebSocket path would require coordinated changes to:

1. `contracts/device-stream.schema.json` and the `FrameMeta` model so the advertised MIME type can be `image/jxl`.
2. The dashboard or companion phone to actually encode JXL. Browser Canvas does not guarantee this encoder; a phone-side encoder or a bundled WebAssembly/native encoder may be necessary.
3. `lounge-control`/`face-worker` validation and media types, currently restricted to `image/jpeg`.
4. The face-worker decoder. Either validate that the pinned OpenCV wheel is built with JXL support on both ARM64 and x86-64, or add and maintain a separate `libjxl` decoder integration. Convert to the pixel array needed by the existing model without persisting the source frame.
5. The crop response contract and clients only if JXL crops are also desired. That is a separate decision from the input frame format.

The feature must preserve the existing frame size bound and transient-memory behavior. Lossy JXL should also be evaluated against recognition quality; a smaller image does not guarantee identical face detector or embedding results.

## Practical decision

For this POC, JPEG already traverses the browser, WebSocket, lounge-control, and OpenCV path. JXL may save bytes, especially for high-fidelity or lossless photographic imagery, but the POC has not measured a network bottleneck or tested JXL decoding in its actual OpenCV wheel. Preserve JPEG compatibility and first get the multi-person results working end to end. If later measurements justify JXL, run a controlled side-by-side on the same source frames and compare compressed bytes, phone encode time, Docker decode time, face detections/matches, and capture-to-result latency before changing the public format.

## Sources

- [ISO/IEC 18181 format overview in the libjxl reference implementation](https://github.com/libjxl/libjxl/blob/main/doc/format_overview.md)
- [libjxl reference implementation: JPEG input/output and lossless JPEG reconstruction](https://github.com/libjxl/libjxl)
- [Apple Safari 17 release notes](https://developer.apple.com/documentation/safari-release-notes/safari-17-release-notes)
- [Chrome 155 JPEG XL decoding announcement](https://developer.chrome.com/blog/jpeg-xl-in-chrome)
- [Firefox 158 stable release notes](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/158)
- [MDN `HTMLCanvasElement.toBlob()` format behavior](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/toBlob)
- [OpenCV image-codec JPEG XL flags](https://docs.opencv.org/doc/doxygen/html/d8/d6a/group__imgcodecs__flags.html)
- [opencv-python wheel build documentation](https://github.com/opencv/opencv-python#manual-builds)
