"""ONNX Runtime execution-provider selection for the face-worker."""

from __future__ import annotations

from typing import Sequence

PROVIDER_MODES = {"cpu", "coreml", "auto"}
COREML_COMPUTE_UNITS = {
    "CPUOnly",
    "CPUAndNeuralEngine",
    "CPUAndGPU",
    "ALL",
}


def select_execution_providers(
    mode: str = "cpu",
    *,
    available_providers: Sequence[str] | None = None,
    coreml_compute_units: str = "CPUAndGPU",
    profile_compute_plan: bool = False,
) -> list[str | tuple[str, dict[str, str]]] | None:
    """Build InsightFace's provider list, keeping CPU as the safe default.

    ``auto`` returns ``None`` so InsightFace/ONNX Runtime can choose from the
    runtime's installed providers. Explicit Core ML mode fails closed when the
    current runtime does not expose its execution provider.
    """
    normalized_mode = mode.strip().lower()
    if normalized_mode not in PROVIDER_MODES:
        raise ValueError(
            "FACE_EXECUTION_PROVIDER must be one of: cpu, coreml, auto"
        )
    if normalized_mode == "cpu":
        return ["CPUExecutionProvider"]
    if normalized_mode == "auto":
        return None

    if coreml_compute_units not in COREML_COMPUTE_UNITS:
        allowed = ", ".join(sorted(COREML_COMPUTE_UNITS))
        raise ValueError(f"COREML_COMPUTE_UNITS must be one of: {allowed}")

    if available_providers is None:
        try:
            import onnxruntime
        except ImportError as exc:
            raise RuntimeError(
                "CoreMLExecutionProvider is unavailable because onnxruntime "
                "could not be imported"
            ) from exc
        available_providers = onnxruntime.get_available_providers()

    if "CoreMLExecutionProvider" not in available_providers:
        raise RuntimeError(
            "CoreMLExecutionProvider is unavailable in this ONNX Runtime build; "
            "install the macOS ONNX Runtime wheel or use FACE_EXECUTION_PROVIDER=cpu"
        )

    options = {"MLComputeUnits": coreml_compute_units}
    if profile_compute_plan:
        options["ProfileComputePlan"] = "1"
    return [("CoreMLExecutionProvider", options), "CPUExecutionProvider"]
