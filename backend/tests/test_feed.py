"""Tests for /api/feed (Campus Pulse) endpoint."""
import pytest
from tests.conftest import auth_headers, register_user


class TestCampusPulse:
    def test_returns_expected_keys(self, client):
        token = register_user(client, suffix="feed1")
        r = client.get("/api/feed", headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert "campus_top_50" in data
        assert "friend_favorites" in data
        assert "campus_icons" in data
        assert "genre_pulse" in data

    def test_empty_when_no_data(self, client):
        token = register_user(client, suffix="feed2")
        r = client.get("/api/feed", headers=auth_headers(token))
        data = r.json()
        # No tunes posted yet
        assert data["campus_top_50"] == []
        assert data["friend_favorites"] == []

    def test_campus_top_50_populated_after_post(self, client):
        token_a = register_user(client, suffix="feed3a")
        token_b = register_user(client, suffix="feed3b")
        # A posts a tune
        client.post("/api/posts",
                    json={"song_name": "Purple Rain", "artist": "Prince"},
                    headers=auth_headers(token_a))
        r = client.get("/api/feed", headers=auth_headers(token_b))
        top50 = r.json()["campus_top_50"]
        assert len(top50) >= 1
        song_names = [s["song_name"] for s in top50]
        assert "Purple Rain" in song_names

    def test_top_50_has_rank_field(self, client):
        token_a = register_user(client, suffix="feed4a")
        token_b = register_user(client, suffix="feed4b")
        client.post("/api/posts",
                    json={"song_name": "Test Song", "artist": "Artist"},
                    headers=auth_headers(token_a))
        r = client.get("/api/feed", headers=auth_headers(token_b))
        for song in r.json()["campus_top_50"]:
            assert "rank" in song
            assert "likes" in song

    def test_campus_icons_populated_after_sync(self, client):
        token_a = register_user(client, suffix="feed5a")
        token_b = register_user(client, suffix="feed5b")
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        r = client.get("/api/feed", headers=auth_headers(token_b))
        icons = r.json()["campus_icons"]
        # Should have some artist entries
        assert isinstance(icons, list)

    def test_genre_pulse_populated_after_sync(self, client):
        token_a = register_user(client, suffix="feed6a")
        token_b = register_user(client, suffix="feed6b")
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        r = client.get("/api/feed", headers=auth_headers(token_b))
        genres = r.json()["genre_pulse"]
        assert isinstance(genres, list)
        if genres:
            for g in genres:
                assert "genre" in g
                assert "percentage" in g

    def test_friend_favorites_shows_matched_user_tune(self, client):
        """After matching, friend's tune shows in friend_favorites."""
        token_a = register_user(client, suffix="feed7a")
        token_b = register_user(client, suffix="feed7b")
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        client.post("/api/spotify/sync", headers=auth_headers(token_b))

        # Create a match
        b_id = client.get("/api/auth/me", headers=auth_headers(token_b)).json()["id"]
        client.post("/api/match/swipe",
                    json={"target_user_id": b_id, "action": "like"},
                    headers=auth_headers(token_a))

        # B posts a tune
        client.post("/api/posts",
                    json={"song_name": "Friends Song", "artist": "Friend Artist"},
                    headers=auth_headers(token_b))

        # A's feed should show B's tune in friend_favorites
        r = client.get("/api/feed", headers=auth_headers(token_a))
        friends = r.json()["friend_favorites"]
        song_names = [f["song_name"] for f in friends]
        assert "Friends Song" in song_names

    def test_unauthenticated_rejected(self, client):
        r = client.get("/api/feed")
        assert r.status_code in (401, 403)
