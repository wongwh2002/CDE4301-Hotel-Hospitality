"""FastAPI mock hotel service.

Provides synthetic guest profiles and synthetic reference photos
for the Hotel Smart-Glasses POC.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, Response

# Ensure local module directory is in python path
MODULE_DIR = Path(__file__).resolve().parent
REPO_ROOT = MODULE_DIR.parent.parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from contracts.models import LoungeProfile
from db import (
    get_guest_photo_bytes,
    get_guest_profile,
    init_db,
    list_all_guests,
)


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
    """Retrieve synthetic reference photo for candidate template derivation."""
    photo_bytes = get_guest_photo_bytes(guest_ref)
    if not photo_bytes:
        raise HTTPException(status_code=404, detail=f"Photo for guest '{guest_ref}' not found")
    return Response(content=photo_bytes, media_type="image/jpeg")


@app.get("/v1/guests", response_model=List[LoungeProfile], tags=["Lounge Profiles"])
async def list_guests():
    """List all synthetic test guest profiles."""
    return list_all_guests()
