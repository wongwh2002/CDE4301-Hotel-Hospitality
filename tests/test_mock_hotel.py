"""Tests for mock-hotel service."""


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
