# Face enrollment photos and allergy cue

**Research date:** 2026-10-15
**Scope:** A small POC guest registration flow that accepts up to three face photos, plus the lounge cue for a guest with a peanut allergy.

## Recommendation

Keep the existing `buffalo_l` detector and recognizer. There is no separate model needed to show a peanut symbol or to turn a stored allergy into a UI cue. Use a small, explicit text-to-emoji rule map for common allergens; unknown terms remain text-only. This is easier to review than asking a language or vision model to infer a symbol. Use the guest's stored allergy field after the face match identifies the guest. For enrollment, derive one embedding per accepted photo and retain up to three samples for that guest. Start by comparing a query embedding against each sample and taking the best similarity for that guest; calibrate the match threshold and margin with multiple samples before relying on it. This is a supported multi-sample pattern in the current InsightFace Server API, but it is not a claim that the project’s current legacy worker already implements that API. [InsightFace model zoo](https://github.com/deepinsight/insightface/blob/master/python-package/docs/model_zoo.md) · [InsightFace Server enrollment and search API](https://github.com/deepinsight/insightface/blob/master/server/docs/api.md)

## Enrolling up to three photos

- **No new face model is required.** `buffalo_l` already combines face detection and recognition. InsightFace's ArcFace ONNX wrapper aligns a detected face from its landmarks, extracts an embedding, and compares vectors by cosine similarity. The current project can run that existing pipeline once per submitted photo. [InsightFace model zoo](https://github.com/deepinsight/insightface/blob/master/python-package/docs/model_zoo.md) · [ArcFace ONNX implementation](https://github.com/deepinsight/insightface/blob/master/python-package/insightface/model_zoo/arcface_onnx.py)
- **Capture distinct, usable samples:** one face per image, in focus and well lit, with a frontal image plus modest left/right variation. Do not silently choose a face if a photo contains multiple people. InsightFace's current enrollment review supports exactly-one-face validation and can reject samples for face size, detector score, image quality, or pose; its current Python guide also documents a 32-pixel minimum face side for reference photos. Those are current upstream API defaults/examples, not thresholds already present in this POC. [InsightFace Server API](https://github.com/deepinsight/insightface/blob/master/server/docs/api.md) · [InsightFace PersonAnalysis guide](https://github.com/deepinsight/insightface/blob/master/python-package/docs/person_analysis.md)
- **Keep the three embeddings initially instead of averaging them.** This retains pose variation and supports the simple per-person maximum-similarity search that InsightFace Server documents for its multiple `FaceSample`s. NIST likewise describes multi-image enrollment as a fusion problem and explicitly leaves implementations free to combine images into one template or keep multiple feature sets. There is no universal aggregation method established by these sources. [InsightFace Server API](https://github.com/deepinsight/insightface/blob/master/server/docs/api.md) · [NIST FRVT ongoing 1:1 API](https://pages.nist.gov/frvt/api/FRVT_ongoing_11_api.pdf)
- **Recalibrate before using the larger gallery.** The maximum over more templates can change genuine and impostor score distributions; the existing single-photo threshold and margin should not be assumed to hold. Validate with separate enrollment and query captures, including unknown guests, different angles, lighting, distance, and blur. NIST evaluates recognition outcomes across enrollment and probe images rather than treating an embedding score as a universal probability. [NIST FRTE/FATE evaluations](https://pages.nist.gov/frvt/)

## Peanut allergy cue

Unicode defines `🥜` (U+1F95C) as **PEANUTS**. Use it as a quick visual aid inside a red warning badge, while keeping the explicit label `PEANUT ALLERGY` and a warning symbol visible. W3C guidance says color should not be the only way to convey meaning, so the warning must remain understandable if red is not perceived or the emoji renders differently. [Unicode character list](https://www.unicode.org/Public/UCD/latest/charts/nameslist/1f900/) · [W3C WAI: do not use color alone](https://www.w3.org/WAI/tips/designing/)

Suggested lounge cue:

```tex
🟢 ✅ ALEX · 🔴 ⚠️ 🥜 PEANUT ALLERGY
```

The face model only proposes the guest identity. The allergy text comes from that guest's hotel profile; the model does not infer allergies from their appearance or photo.

## Implementation implications for this POC

1. Let registration upload or capture 1–3 JPEGs, show each preview, and allow retakes before submitting.
2. Validate each image independently. Reject a sample with no face or more than one face; show which image needs replacement. Keep the system working if fewer than three good photos are available.
3. Store/reference the accepted photos or their embeddings under the guest identity. If storing source photos for later re-enrollment, make that behavior clear in the POC UI.
4. On a query frame, compare the query embedding with each stored sample for each active guest, retain the strongest score per guest, then apply the existing threshold, runner-up margin, and temporal stability policy after they are calibrated for multi-image enrollment.
5. Render allergy as text plus warning shape/symbol and color. Keep `🥜` decorative/supporting; do not rely on its exact color or shape across devices.

## Sources

- [InsightFace model zoo](https://github.com/deepinsight/insightface/blob/master/python-package/docs/model_zoo.md)
- [InsightFace ArcFace ONNX implementation](https://github.com/deepinsight/insightface/blob/master/python-package/insightface/model_zoo/arcface_onnx.py)
- [InsightFace PersonAnalysis guide](https://github.com/deepinsight/insightface/blob/master/python-package/docs/person_analysis.md)
- [InsightFace Server API](https://github.com/deepinsight/insightface/blob/master/server/docs/api.md)
- [NIST FRVT ongoing 1:1 API](https://pages.nist.gov/frvt/api/FRVT_ongoing_11_api.pdf)
- [NIST Face Technology Evaluations](https://pages.nist.gov/frvt/)
- [Unicode Supplemental Symbols and Pictographs chart](https://www.unicode.org/Public/UCD/latest/charts/nameslist/1f900/)
- [W3C WAI: Designing for Web Accessibility](https://www.w3.org/WAI/tips/designing/)
