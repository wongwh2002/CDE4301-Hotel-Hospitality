"""Pytest configuration and fixtures for Hotel Smart-Glasses POC."""

import importlib.util
import os
import sys
from pathlib import Path
import pytest
from starlette.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Set test environment variables
os.environ["SQLITE_PATH"] = ":memory:"
os.environ["DEVICE_AUTH_TOKEN"] = "test-secret-token"
os.environ["INTERNAL_API_TOKEN"] = "test-internal-token"
os.environ["COHORT_EXPIRY_SECONDS"] = "3600"
os.environ["MAX_FRAME_SIZE_BYTES"] = "1048576"  # 1 MB for testing
os.environ["QUEUE_MAXSIZE"] = "3"
os.environ["FACE_RECOGNITION_ENABLED"] = "false"


def load_app(app_name: str):
    """Dynamically load FastAPI app instance from apps/<app_name>/main.py."""
    app_dir = REPO_ROOT / "apps" / app_name
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

    main_path = app_dir / "main.py"
    module_name = f"apps_{app_name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, main_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.app


@pytest.fixture
def mock_hotel_client(tmp_path, monkeypatch):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "mock-hotel.db"))
    app = load_app("mock-hotel")
    with TestClient(app) as client:
        yield client


@pytest.fixture
def face_worker_client():
    app = load_app("face-worker")
    with TestClient(app, headers={"X-Internal-Token": "test-internal-token"}) as client:
        yield client


@pytest.fixture
def lounge_control_client():
    app = load_app("lounge-control")
    with TestClient(app, headers={"X-Internal-Token": "test-internal-token"}) as client:
        yield client
