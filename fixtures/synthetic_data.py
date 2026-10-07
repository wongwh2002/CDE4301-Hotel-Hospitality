"""Synthetic test fixtures for Hotel Smart-Glasses POC.

Provides valid synthetic JPEG data and profile fixtures.
Never contains real guest photographs, biometrics, or personal data.
"""

import base64
from pathlib import Path
from typing import Optional

# Tiny valid JPEG containing a solid-color synthetic image; no person is depicted.
SYNTHETIC_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a"
    "HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy"
    "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAACAAIDASIA"
    "AhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAA"
    "AF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3OD"
    "k6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6i"
    "pqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEB"
    "AQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQ"
    "dhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldW"
    "V1hZWmNkZWZnaGlqc3R1dnd4eXqCgoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6ws"
    "PExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDm6KKK4T5k/9k="
)

SYNTHETIC_JPEG_BYTES = base64.b64decode(SYNTHETIC_JPEG_B64)

FIXTURE_DIR = Path(__file__).resolve().parent
FIXTURE_FRAME_PATH = FIXTURE_DIR / "synthetic_frame.jpg"


def ensure_fixture_frame(path: Optional[Path] = None) -> Path:
    """Write the synthetic JPEG to an explicit path (or the default fixture path)."""
    target = path or FIXTURE_FRAME_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(SYNTHETIC_JPEG_BYTES)
    return target
