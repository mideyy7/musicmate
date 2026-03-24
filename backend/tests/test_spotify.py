"""Tests for /api/spotify endpoints (mock mode)."""
import pytest
from tests.conftest import auth_headers, register_user


class TestSpotifyAuthUrl:
    def test_returns_mock_url_in_mock_mode(self, client):
        token = register_user(client, suffix="spotauth")
        r = client.get("/api/spotify/auth-url", headers=auth_headers(token))
        assert r.status_code == 200
        assert "auth_url" in r.json()
        # In mock mode we return a placeholder URL
        assert r.json()["auth_url"] == "mock://spotify/authorize"

    def test_unauthenticated_rejected(self, client):
        r = client.get("/api/spotify/auth-url")
        assert r.status_code in (401, 403)


class TestSpotifyCallback:
    def test_mock_callback_stores_tokens(self, client):
        token = register_user(client, suffix="spotcb")
        r = client.post("/api/spotify/callback", json={"code": "mockcode123"},
                        headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert data["connected"] is True
        assert data["spotify_user_id"] is not None


class TestSpotifyStatus:
    def test_mock_mode_auto_creates_profile(self, client):
        token = register_user(client, suffix="spotstatus")
        r = client.get("/api/spotify/status", headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert data["connected"] is True
        assert data["spotify_user_id"] is not None

    def test_unauthenticated_rejected(self, client):
        r = client.get("/api/spotify/status")
        assert r.status_code in (401, 403)


class TestSpotifySync:
    def test_sync_generates_mock_profile(self, client):
        token = register_user(client, suffix="spotsync")
        r = client.post("/api/spotify/sync", headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert "top_artists" in data
        assert "top_genres" in data
        assert "recent_tracks" in data
        assert "listening_patterns" in data
        assert len(data["top_artists"]) > 0
        assert len(data["top_genres"]) > 0

    def test_mock_profile_has_valid_structure(self, client):
        token = register_user(client, suffix="spotsync2")
        r = client.post("/api/spotify/sync", headers=auth_headers(token))
        data = r.json()
        # Verify artist structure
        for artist in data["top_artists"]:
            assert "name" in artist

    def test_sync_idempotent(self, client):
        """Syncing twice should succeed both times and update the profile."""
        token = register_user(client, suffix="syncidm")
        r1 = client.post("/api/spotify/sync", headers=auth_headers(token))
        r2 = client.post("/api/spotify/sync", headers=auth_headers(token))
        assert r1.status_code == 200
        assert r2.status_code == 200


class TestSpotifyProfile:
    def test_profile_returned_after_sync(self, client):
        token = register_user(client, suffix="spotprof")
        client.post("/api/spotify/sync", headers=auth_headers(token))
        r = client.get("/api/spotify/profile", headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert "top_artists" in data

    def test_profile_404_before_sync(self, client):
        token = register_user(client, suffix="spotprof2")
        r = client.get("/api/spotify/profile", headers=auth_headers(token))
        assert r.status_code == 404


class TestSpotifyDisconnect:
    def test_disconnect_removes_profile(self, client):
        token = register_user(client, suffix="spotdisc")
        # Sync first to create a profile
        client.post("/api/spotify/sync", headers=auth_headers(token))
        # Disconnect
        r = client.delete("/api/spotify/disconnect", headers=auth_headers(token))
        assert r.status_code == 200
        assert "disconnected" in r.json()["message"].lower()
        # Profile should be gone
        r2 = client.get("/api/spotify/profile", headers=auth_headers(token))
        assert r2.status_code == 404

    def test_disconnect_idempotent(self, client):
        """Disconnecting when not connected should not crash."""
        token = register_user(client, suffix="spotdisc2")
        r = client.delete("/api/spotify/disconnect", headers=auth_headers(token))
        assert r.status_code == 200
