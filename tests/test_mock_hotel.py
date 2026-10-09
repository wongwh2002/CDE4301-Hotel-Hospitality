"""Tests for mock-hotel service."""

from fixtures.synthetic_data import SYNTHETIC_FACE_JPEG_BYTES, SYNTHETIC_JPEG_BYTES


def test_mock_hotel_health(mock_hotel_client):
    """Test healthcheck endpoint."""
    resp = mock_hotel_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "mock-hotel"


def test_get_lounge_profile(mock_hotel_client):
    """Test retrieving synthetic guest profile."""
    resp = mock_hotel_client.get("/v1/guests/guest-alex-101/lounge-profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["guest_ref"] == "guest-alex-101"
    assert data["display_name"] == "Alex"
    assert data["room_number"] == "401"
    assert "Peanut allergy" in data["allergies"]


def test_get_guest_photo(mock_hotel_client):
    """Test retrieving synthetic reference photo."""
    resp = mock_hotel_client.get("/v1/guests/guest-alex-101/photo")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/jpeg"
    content = resp.content
    assert len(content) > 0
    # Must have JPEG SOI and EOI markers
    assert content[0] == 0xFF and content[1] == 0xD8
    assert content[-2] == 0xFF and content[-1] == 0xD9


def test_seeded_face_fixture_is_limited_to_alex(mock_hotel_client):
    """Keep one fictional face for the local recognition smoke demo only."""
    alex_photo = mock_hotel_client.get("/v1/guests/guest-alex-101/photo")
    jordan_photo = mock_hotel_client.get("/v1/guests/guest-jordan-102/photo")

    assert alex_photo.content == SYNTHETIC_FACE_JPEG_BYTES
    assert jordan_photo.content == SYNTHETIC_JPEG_BYTES


def test_get_unknown_guest_profile_404(mock_hotel_client):
    """Test 404 returned for unknown guest reference."""
    resp = mock_hotel_client.get("/v1/guests/guest-nonexistent-999/lounge-profile")
    assert resp.status_code == 404


def test_list_synthetic_guests(mock_hotel_client):
    """Test listing all synthetic test profiles."""
    resp = mock_hotel_client.get("/v1/guests")
    assert resp.status_code == 200
    guests = resp.json()
    assert len(guests) >= 4
    refs = [g["guest_ref"] for g in guests]
    assert "guest-alex-101" in refs
    assert "guest-jordan-102" in refs


def test_register_guest_success(mock_hotel_client):
    """Test registering a new synthetic guest profile."""
    payload = {
        "display_name": "Taylor",
        "room_number": "702",
        "vip_tier": "Diamond",
        "allergies": ["Dairy allergy"],
        "preferences": ["Still water", "Corner table"],
    }
    resp = mock_hotel_client.post("/v1/guests", json=payload)
    assert resp.status_code == 201
    data = resp.json()

    assert data["display_name"] == "Taylor"
    assert data["room_number"] == "702"
    assert data["vip_tier"] == "Diamond"
    assert data["allergies"] == ["Dairy allergy"]
    assert data["preferences"] == ["Still water", "Corner table"]
    assert "guest_ref" in data
    assert data["guest_ref"].startswith("guest-taylor-")
    assert data["photo_url"] == f"/v1/guests/{data['guest_ref']}/photo"

    guest_ref = data["guest_ref"]

    # Verify guest profile can be fetched
    profile_resp = mock_hotel_client.get(f"/v1/guests/{guest_ref}/lounge-profile")
    assert profile_resp.status_code == 200
    profile = profile_resp.json()
    assert profile["guest_ref"] == guest_ref
    assert profile["display_name"] == "Taylor"

    # Verify synthetic photo can be fetched
    photo_resp = mock_hotel_client.get(f"/v1/guests/{guest_ref}/photo")
    assert photo_resp.status_code == 200
    assert photo_resp.headers["content-type"] == "image/jpeg"
    assert len(photo_resp.content) > 0

    # Verify guest appears in list
    list_resp = mock_hotel_client.get("/v1/guests")
    assert list_resp.status_code == 200
    all_refs = [g["guest_ref"] for g in list_resp.json()]
    assert guest_ref in all_refs


def test_register_guest_validation(mock_hotel_client):
    """Test validation errors for required display_name and optional fields."""
    # Missing display_name
    resp = mock_hotel_client.post("/v1/guests", json={"room_number": "101"})
    assert resp.status_code == 422

    # Empty display_name
    resp_empty = mock_hotel_client.post("/v1/guests", json={"display_name": "   "})
    assert resp_empty.status_code == 422

    # Minimal registration with only required display_name
    minimal_resp = mock_hotel_client.post("/v1/guests", json={"display_name": "Morgan"})
    assert minimal_resp.status_code == 201
    minimal_data = minimal_resp.json()
    assert minimal_data["display_name"] == "Morgan"
    assert minimal_data["allergies"] == []
    assert minimal_data["preferences"] == []
    assert minimal_data["room_number"] is None
    assert minimal_data["guest_ref"].startswith("guest-morgan-")
