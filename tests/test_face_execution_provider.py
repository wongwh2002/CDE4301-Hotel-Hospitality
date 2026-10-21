import pytest
from types import SimpleNamespace

from execution_provider import select_execution_providers
from vision import InsightFaceEngine


def test_cpu_is_the_default_and_only_selects_cpu():
    assert select_execution_providers() == ["CPUExecutionProvider"]


def test_auto_leaves_provider_selection_to_insightface():
    assert select_execution_providers("auto") is None


def test_coreml_uses_neural_engine_with_cpu_fallback():
    providers = select_execution_providers(
        "coreml",
        available_providers=["CoreMLExecutionProvider", "CPUExecutionProvider"],
    )

    assert providers == [
        (
            "CoreMLExecutionProvider",
            {"MLComputeUnits": "CPUAndGPU"},
        ),
        "CPUExecutionProvider",
    ]


def test_coreml_can_request_compute_plan_profile():
    providers = select_execution_providers(
        "coreml",
        available_providers=["CoreMLExecutionProvider", "CPUExecutionProvider"],
        profile_compute_plan=True,
    )

    assert providers[0][1]["ProfileComputePlan"] == "1"


def test_coreml_requires_available_provider():
    with pytest.raises(RuntimeError, match="CoreMLExecutionProvider is unavailable"):
        select_execution_providers(
            "coreml", available_providers=["CPUExecutionProvider"]
        )


def test_invalid_provider_mode_is_rejected():
    with pytest.raises(ValueError, match="FACE_EXECUTION_PROVIDER"):
        select_execution_providers("gpu")


def test_invalid_compute_units_are_rejected():
    with pytest.raises(ValueError, match="COREML_COMPUTE_UNITS"):
        select_execution_providers(
            "coreml",
            available_providers=["CoreMLExecutionProvider", "CPUExecutionProvider"],
            coreml_compute_units="NeuralEngineOnly",
        )


def test_session_provider_report_collects_every_loaded_model():
    class Session:
        def __init__(self, providers):
            self.providers = providers

        def get_providers(self):
            return self.providers

    analysis = SimpleNamespace(
        models={
            "detection": SimpleNamespace(
                session=Session(["CoreMLExecutionProvider", "CPUExecutionProvider"])
            ),
            "recognition": SimpleNamespace(
                session=Session(["CPUExecutionProvider"])
            ),
        }
    )

    assert InsightFaceEngine._session_providers_by_model(analysis) == {
        "detection": ["CoreMLExecutionProvider", "CPUExecutionProvider"],
        "recognition": ["CPUExecutionProvider"],
    }
