"""FastAPI mock hotel service.

Provides synthetic guest profiles and local reference-photo storage for the
Hotel Smart-Glasses POC.
"""

import base64
import binascii
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, Response, status

# Ensure local module directory is in python path
MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.models import GuestRegistrationRequest, LoungeProfile
from db import (
    get_guest_photo_bytes,
    get_guest_profile,
    init_db,
    list_all_guests,
    register_guest,
)

MAX_REFERENCE_PHOTO_BYTES = 2 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed SQLite synthetic database on startup
    init_db()
    yield


app = FastAPI(
    title="Mock Hotel Profile API",
    description="Synthetic hotel guest profile service for local POC development",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint for Docker Compose."""
    return {"status": "ok", "service": "mock-hotel"}


@app.get(
    "/v1/guests/{guest_ref}/lounge-profile",
    response_model=LoungeProfile,
    tags=["Lounge Profiles"],
)
async def get_lounge_profile(guest_ref: str):
    """Retrieve minimal permitted guest profile for lounge operations."""
    profile = get_guest_profile(guest_ref)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Guest reference '{guest_ref}' not found")
    return profile


@app.get("/v1/guests/{guest_ref}/photo", tags=["Lounge Profiles"])
async def get_guest_photo(guest_ref: str):
    """Retrieve the primary reference photo for candidate template derivation."""
    photo_bytes = get_guest_photo_bytes(guest_ref)
    if not photo_bytes:
        raise HTTPException(status_code=404, detail=f"Photo for guest '{guest_ref}' not found")
    return Response(content=photo_bytes, media_type="image/jpeg")


@app.get("/v1/guests/{guest_ref}/photos/{photo_index}", tags=["Lounge Profiles"])
async def get_guest_reference_photo(guest_ref: str, photo_index: int):
    """Retrieve one indexed reference photo for face-template enrollment."""
    if photo_index < 0 or photo_index > 2:
        raise HTTPException(status_code=404, detail="Reference photo not found")
    photo_bytes = get_guest_photo_bytes(guest_ref, photo_index)
    if not photo_bytes:
        raise HTTPException(status_code=404, detail="Reference photo not found")
    return Response(content=photo_bytes, media_type="image/jpeg")


@app.get("/v1/guests", response_model=List[LoungeProfile], tags=["Lounge Profiles"])
async def list_guests():
    """List all synthetic test guest profiles."""
    return list_all_guests()


@app.post(
    "/v1/guests",
    response_model=LoungeProfile,
    status_code=status.HTTP_201_CREATED,
    tags=["Lounge Profiles"],
)
async def register_new_guest(request: GuestRegistrationRequest):
    """Register a synthetic guest with up to three optional reference photos."""
    clean_display_name = request.display_name.strip()
    if not clean_display_name:
        raise HTTPException(status_code=422, detail="display_name cannot be empty")
    photo_bytes_list = []
    for index, photo_b64 in enumerate(request.photos_b64):
        try:
            photo_bytes = base64.b64decode(photo_b64, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Reference photo {index + 1} is not valid base64",
            ) from exc
        if len(photo_bytes) > MAX_REFERENCE_PHOTO_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Reference photo {index + 1} exceeds the 2 MiB limit",
            )
        if (
            len(photo_bytes) < 4
            or photo_bytes[:2] != b"\xff\xd8"
            or photo_bytes[-2:] != b"\xff\xd9"
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Reference photo {index + 1} must be a JPEG image",
            )
        photo_bytes_list.append(photo_bytes)

    profile = register_guest(
        display_name=clean_display_name,
        allergies=request.allergies,
        preferences=request.preferences,
        room_number=request.room_number,
        vip_tier=request.vip_tier,
        photo_bytes_list=photo_bytes_list,
    )
    return profile
