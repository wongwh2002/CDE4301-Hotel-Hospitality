# JPEG XL for the lounge POC image path

**Checked:** 2026-10-19
**Scope:** Whether `.jxl` should replace JPEG for guest reference photos, phone-to-`lounge-control` frames, and face crops in the current local Docker POC, and the implementation of optional JXL frame input.

## Recommendation

**Keep JPEG as the default, and accept JPEG XL as an optional incoming phone-frame format.** The pinned prebuilt `opencv-python-headless==4.14.0.94` wheel does not decode JXL: both the M1 Python environment and the Linux arm64 Docker wheel returned `None` from `cv2.imdecode()` for a real JXL. The Docker image now builds a custom headless OpenCV wheel against system libjxl; a generated lossless JXL decoded through `cv2.imdecode()` to the expected BGR pixel in an isolated Linux arm64 container. `imagecodecs==2026.10.10` remains as a fallback for local environments whose prebuilt OpenCV wheel lacks JXL. The dashboard, replay client, reference photos, and returned face crops remain JPEG. This is format-path support, not evidence that JXL improves POC accuracy or latency.

Implementation: `DeviceStreamMessage.format` accepts `image/jpeg` or `image/jxl`; lounge-control preserves the MIME type on its internal handoff; face-worker validates the declared encoding and prefers OpenCV's libjxl-backed decoder, with `imagecodecs` fallback. Pytest exercises JXL validation, BGR conversion, frame intake, and MIME-type forwarding. Compose CI checks direct `cv2.imdecode()` in the built face-worker image and posts a JXL through actual HTTP intake. Keep the JPEG path as the reproducible baseline until real phone measurements compare payload size, phone encode time, worker decode time, face detections/matches, and end-to-end latency.

## How this repo handles images today

- Before the current implementation, the device-stream contract fixed frame `format` to `image/jpeg` and lounge-control forwarded those bytes to face-worker. The contract now accepts `image/jpeg` and `image/jxl` for incoming frames. ([device-stream schema](../../contracts/device-stream.schema.json), [contract models](../../contracts/models.py), [lounge-control frame path](../../apps/lounge-control/main.py))
- Before the current implementation, face-worker accepted only `Content-Type: image/jpeg`; it continues to use `cv2.imdecode()` for JPEG. The worker now prefers the custom OpenCV JXL decoder, with `imagecodecs` fallback. Face crops remain `.jpg`, and the crop contract still uses `image/jpeg`. ([face-worker ingress](../../apps/face-worker/main.py), [vision decoder and crop encoder](../../apps/face-worker/vision.py), [face-crop schema](../../contracts/face-crop.schema.json))
- The dashboard file input lists JPEG, PNG, and WebP, then its camera/frame path uses `canvas.toBlob(..., 'image/jpeg', 0.82)`. It sends a `frame_meta` format of `image/jpeg`. ([dashboard input and encoder](../../apps/lounge-control/dashboard.py))
- The face-worker pins `opencv-python-headless==4.14.0.94`. The regular M1 and Linux arm64 wheels did not list JPEG XL in `cv2.getBuildInformation()`, and `cv2.imdecode()` returned `None` for a real JXL sample. The Dockerfile now builds a custom Linux OpenCV wheel against `libjxl-dev`; an isolated Linux arm64 build produced a JPEG XL build-info entry and decoded a JXL sample with `cv2.imdecode()`. At runtime the image installs `libjxl0.11`, which supplies the linked decoder libraries. The application keeps pinned `imagecodecs==2026.10.10` as a fallback for host Python environments and for validating JXL payloads. ([OpenCV imgcodecs build configuration](https://github.com/opencv/opencv/blob/4.x/modules/imgcodecs/CMakeLists.txt), [OpenCV Python wheel build notes](https://github.com/opencv/opencv-python#manual-builds), [imagecodecs JPEG XL API](https://github.com/cgohlke/imagecodecs/blob/master/imagecodecs/_jpegxl.pyx), [imagecodecs platform and Python support](https://github.com/cgohlke/imagecodecs))

### Can OpenCV itself decode JXL?

Yes, if the OpenCV binary was built with JPEG XL. The build gate is `WITH_JPEGXL=ON` **and** a system `libjxl` development installation that CMake can find (including `jxl/decode.h` and the library); OpenCV does not bundle libjxl, and `BUILD_JPEGXL` is unsupported. The decoder is compiled under `HAVE_JPEGXL`, so this is a build-time capability, not something a runtime environment variable can switch on. ([OpenCV configuration reference](https://docs.opencv.org/4.13.0/db/d05/tutorial_config_reference.html), [OpenCV's libjxl finder](https://github.com/opencv/opencv/blob/4.x/cmake/OpenCVFindJPEGXL.cmake), [JPEG XL decoder compile guard](https://github.com/opencv/opencv/blob/4.x/modules/imgcodecs/src/grfmt_jpegxl.cpp))

For a custom OpenCV Python build, install the platform's libjxl development package before configuring (for example, Debian/Ubuntu's `libjxl-dev`), enable `-DWITH_JPEGXL=ON`, and check the CMake/OpenCV build summary for a found system JPEG-XL library. Add `-DENABLE_CONFIG_VERIFICATION=ON` if you want CMake to fail when an enabled dependency is unavailable, instead of silently producing a build without that codec. The upstream `opencv-python` project supports passing custom CMake options when building wheels, but its published wheel name/version does not promise JXL; test the actual wheel you plan to ship. Its documentation describes wheels as prebuilt OpenCV binaries and documents `CMAKE_ARGS` for custom source builds. A current alternate binary recipe, conda-forge, explicitly depends on `libjxl` and sets `WITH_JPEGXL=1`; still verify the selected platform package. ([OpenCV configuration reference](https://docs.opencv.org/4.13.0/db/d05/tutorial_config_reference.html), [Debian `libjxl-dev` package](https://packages.debian.org/stable/libdevel/libjxl-dev), [opencv-python build documentation](https://github.com/opencv/opencv-python#manual-builds), [conda-forge OpenCV recipe](https://github.com/conda-forge/opencv-feedstock/blob/main/recipe/build.sh), [conda-forge runtime dependencies](https://github.com/conda-forge/opencv-feedstock/blob/main/recipe/meta.yaml))

For example, from a checked-out `opencv-python` source tree after installing the JXL development package:

```sh
CMAKE_ARGS="-DWITH_JPEGXL=ON -DENABLE_CONFIG_VERIFICATION=ON" \
  ENABLE_HEADLESS=1 python -m pip wheel . --verbose
```

Install the resulting custom wheel in the runtime image and make sure its linked libjxl runtime libraries are available (or were bundled into the wheel). Build and test separately for each OS, architecture, and Python ABI you intend to ship.

Verify the imported `cv2` binary and an actual JXL file; `getBuildInformation()` alone does not prove that the sample decodes:

```python
import cv2
import numpy as np

print("\n".join(
    line for line in cv2.getBuildInformation().splitlines()
    if "JPEG XL" in line
))

encoded = np.fromfile("sample.jxl", dtype=np.uint8)  # A real JXL file
image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
assert image is not None and image.size, "This cv2 build did not decode sample.jxl"
print(image.shape, image.dtype)
```

Run this inside the same Docker image/environment used by face-worker to verify the production decoder. This repo now builds the Docker OpenCV wheel with JXL support; `imagecodecs` remains the fallback for local environments using the stock wheel.

## Format and client compatibility

JPEG XL is standardized as ISO/IEC 18181. The official JPEG Committee describes lossy coding, lossless coding, lossless JPEG recompression, HDR, alpha, animation, and progressive coding as format features. The libjxl reference documentation describes two pixel coding modes: VarDCT for lossy photo coding and Modular for lossless or lossy coding. JXL's lossless JPEG transcoding can preserve/reconstruct the exact original JPEG file; it does not restore detail previously discarded by JPEG. ([JPEG Committee JPEG XL overview](https://jpeg.org/jpegxl/index.html), [libjxl format overview](https://github.com/libjxl/libjxl/blob/main/doc/format_overview.md))

### JPEG vs. JPEG XL for this POC

| Area | JPEG (current path) | JPEG XL (candidate) | POC impact |
| --- | --- | --- | --- |
| Compression | Conventional phone/browser JPEG is lossy. The JFIF profile commonly used for images has one or three components and 8-bit samples per component. | Offers lossy and lossless modes; also supports lossless recompression of an existing JPEG. The JPEG Committee states JXL offers better compression, but the byte savings depend on source pixels, quality/effort settings, and encoder. | JXL may reduce upload size at similar visual quality, but no savings have been measured on this POC's camera frames. A lossless transcode of JPEG can preserve the original JPEG data but cannot recover information already lost. |
| Pixel fidelity and CV input | The current browser path sends JPEG at quality 0.82. It is decoded to pixels before face inference. | Lossy JXL may produce different pixels from JPEG; lossless JXL can preserve source pixel values. JXL's wider bit-depth, HDR, and gamut support are available but unnecessary for this 8-bit face-recognition path. | Recognition is sensitive to face detail, so compare detected faces, similarity scores, and stable matches—not just visual appearance or file size. |
| Alpha, animation, and progressive coding | The usual JFIF phone JPEG path is a still image without an alpha channel. JPEG does have progressive coding modes. | Supports alpha, animation, and progressive/partial decoding. | These features do not help the present protocol: it sends complete still-frame payloads and runs CV on decoded pixels. Animation would not replace the current WebSocket frame loop. |
| Compatibility and MIME | `image/jpeg` is already used by the wire schema, face-worker ingress, output crop contract, dashboard, and test fixture path. | IANA registers `image/jxl`; a client/server must explicitly negotiate and handle it. | Changing only a file extension or `frame_meta.format` is insufficient; all validators and decoders must agree on the actual bytes and MIME type. |
| Browser and phone encoding | The dashboard calls `canvas.toBlob(..., 'image/jpeg', 0.82)`. JPEG is the current, exercised encoder path. | Browsers may decode JXL without exposing a JXL encoder. The HTML standard says unsupported `toBlob()` types fall back to PNG, so a caller must check the returned blob type. A native phone app could use a JXL encoder library, but that adds an integration and performance dependency. | Chrome's announced Chrome 155 support is explicitly decoding support; it does not establish `canvas.toBlob('image/jxl')` support. The UI would need a real encoder or a safe fallback. |
| OpenCV / Docker decoding | The published pinned wheel does not decode JXL on macOS arm64 or Linux arm64. | OpenCV can use libjxl when compiled with the JXL dependency; the custom Docker wheel now uses `cv2.imdecode()`. `imagecodecs` remains the local fallback. | OpenCV's custom source build took about eight minutes and depends on libjxl at runtime. The project Docker build and direct decode check passed on Linux arm64; the amd64 CI run is still pending. |

Baseline JPEG here means the common JFIF/browser/phone profile, not every process described by the wider JPEG standard. The [ITU-T JFIF recommendation](https://www.itu.int/rec/T-REC-T.871/en) specifies the familiar 1- or 3-component interchange path. JXL's added HDR, alpha, animation, and progressive capabilities are real spec differences, but they do not directly improve recognition when the worker ultimately needs an ordinary pixel array.

Browser decoder support has improved recently:

| Client | Status at check date | What it means here |
| --- | --- | --- |
| Safari | Apple lists JPEG XL support starting in Safari 17. | A browser may display JXL, but the companion phone and Docker CV decoder still need independent support. |
| Chrome | Chrome announced built-in JPEG XL **decoding** starting with Chrome 155. | This is decode support, not an announced browser Canvas encoder for the dashboard's outgoing frames. |
| Firefox | Firefox 158 stable, released 2026-10-13, enabled `image/jxl` by default. | Recent Firefox clients can decode JXL; older releases and other embedded WebViews may differ. |

Sources: [Safari 17 release notes](https://developer.apple.com/documentation/safari-release-notes/safari-17-release-notes), [Chrome: Shipping JPEG XL in Chrome](https://developer.chrome.com/blog/jpeg-xl-in-chrome), [Firefox 158 release notes](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/158).

The Canvas `toBlob()` API emits the requested format only if that user agent supports that encoder; otherwise it falls back to PNG. The current dashboard explicitly asks for JPEG. Do not infer JXL **encoding** support from a browser's ability to decode JXL. ([WHATWG HTML Canvas serialization rules](https://html.spec.whatwg.org/multipage/canvas.html#dom-canvas-toblob-dev))

## What adopting JXL would require

Sending JXL bytes through the existing raw binary WebSocket path would require coordinated changes to:

1. `contracts/device-stream.schema.json` and the `FrameMeta` model so the advertised MIME type can be `image/jxl`.
2. The dashboard or companion phone to actually encode JXL. Browser Canvas does not guarantee this encoder; a phone-side encoder or a bundled WebAssembly/native encoder may be necessary.
3. `lounge-control`/`face-worker` validation and MIME forwarding. These now accept JXL for incoming frames while preserving JPEG clients.
4. The face-worker decoder. The Docker build installs libjxl development/runtime libraries and builds OpenCV with `WITH_JPEGXL=ON`; the service prefers `cv2.imdecode()` and keeps `imagecodecs` as a fallback. Convert to the pixel array needed by the existing model without persisting the source frame.
5. The crop response contract and clients only if JXL crops are also desired. That is a separate decision from the input frame format; this POC keeps face crops as JPEG.

The feature must preserve the existing frame size bound and transient-memory behavior. Lossy JXL should also be evaluated against recognition quality; a smaller image does not guarantee identical face detector or embedding results.

## Practical decision

JPEG remains the default because it is the only format currently emitted by the dashboard and replay client, and JXL phone encoding and POC-level benefits have not been measured. The worker can accept JXL from a client with a real JXL encoder, and the custom Docker OpenCV build decoded a lossless sample on Linux arm64. The amd64 CI build remains to be confirmed before relying on it for another platform. Before changing a phone client, compare identical frames for payload size, phone encode time, worker decode time, face detections and matches, and capture-to-result latency. JXL input support does not change guest photo storage or JPEG crop output.

## Sources

- [ISO/IEC 18181 format overview in the libjxl reference implementation](https://github.com/libjxl/libjxl/blob/main/doc/format_overview.md)
- [JPEG Committee JPEG XL overview and features](https://jpeg.org/jpegxl/index.html)
- [libjxl reference implementation: JPEG input/output and lossless JPEG reconstruction](https://github.com/libjxl/libjxl)
- [ITU-T T.81 JPEG coding standard](https://www.itu.int/rec/T-REC-T.81/en)
- [ITU-T T.871 JFIF recommendation](https://www.itu.int/rec/T-REC-T.871/en)
- [IANA media-type registry (`image/jpeg` and `image/jxl`)](https://www.iana.org/assignments/media-types)
- [Apple Safari 17 release notes](https://developer.apple.com/documentation/safari-release-notes/safari-17-release-notes)
- [Chrome 155 JPEG XL decoding announcement](https://developer.chrome.com/blog/jpeg-xl-in-chrome)
- [Firefox 158 stable release notes](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/158)
- [WHATWG HTML Canvas serialization rules](https://html.spec.whatwg.org/multipage/canvas.html#dom-canvas-toblob-dev)
- [OpenCV image-codec JPEG XL flags](https://docs.opencv.org/doc/doxygen/html/d8/d6a/group__imgcodecs__flags.html)
- [OpenCV imgcodecs build configuration (optional libjxl dependency)](https://github.com/opencv/opencv/blob/4.x/modules/imgcodecs/CMakeLists.txt)
- [OpenCV configuration reference (`WITH_JPEGXL`, system libjxl requirement)](https://docs.opencv.org/4.13.0/db/d05/tutorial_config_reference.html)
- [OpenCV CMake libjxl finder](https://github.com/opencv/opencv/blob/4.x/cmake/OpenCVFindJPEGXL.cmake)
- [OpenCV JPEG XL decoder implementation](https://github.com/opencv/opencv/blob/4.x/modules/imgcodecs/src/grfmt_jpegxl.cpp)
- [opencv-python wheel build documentation](https://github.com/opencv/opencv-python#manual-builds)
- [conda-forge OpenCV build recipe (`WITH_JPEGXL=1`)](https://github.com/conda-forge/opencv-feedstock/blob/main/recipe/build.sh)
