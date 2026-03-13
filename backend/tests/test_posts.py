"""Tests for /api/posts endpoints (Daily Tunes)."""
import pytest
from tests.conftest import auth_headers, register_user


class TestGetPosts:
    def test_empty_initially(self, client):
        token = register_user(client, suffix="postsget")
        r = client.get("/api/posts", headers=auth_headers(token))
        assert r.status_code == 200
        assert r.json() == []

    def test_unauthenticated_rejected(self, client):
        r = client.get("/api/posts")
        assert r.status_code in (401, 403)


class TestPostTune:
    def test_create_post(self, client):
        token = register_user(client, suffix="posttune")
        r = client.post("/api/posts",
                        json={"song_name": "Blinding Lights", "artist": "The Weeknd"},
                        headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert data["song_name"] == "Blinding Lights"
        assert data["artist"] == "The Weeknd"
        assert data["likes"] == 0
        assert data["dislikes"] == 0
        assert data["my_reaction"] is None

    def test_post_appears_in_feed(self, client):
        token = register_user(client, suffix="postfeed")
        client.post("/api/posts",
                    json={"song_name": "Levitating", "artist": "Dua Lipa"},
                    headers=auth_headers(token))
        r = client.get("/api/posts", headers=auth_headers(token))
        songs = [p["song_name"] for p in r.json()]
        assert "Levitating" in songs

    def test_one_post_per_day_limit(self, client):
        token = register_user(client, suffix="oneperday")
        client.post("/api/posts",
                    json={"song_name": "Song 1", "artist": "Artist A"},
                    headers=auth_headers(token))
        r = client.post("/api/posts",
                        json={"song_name": "Song 2", "artist": "Artist B"},
                        headers=auth_headers(token))
        assert r.status_code == 400
        assert "already posted" in r.json()["detail"].lower()

    def test_post_has_time_ago(self, client):
        token = register_user(client, suffix="timeago")
        r = client.post("/api/posts",
                        json={"song_name": "Test Song", "artist": "Test Artist"},
                        headers=auth_headers(token))
        assert "time_ago" in r.json()

    def test_post_shows_display_name(self, client):
        token = register_user(client, suffix="postname")
        r = client.post("/api/posts",
                        json={"song_name": "Song", "artist": "Artist"},
                        headers=auth_headers(token))
        assert r.json()["display_name"] is not None

    def test_unauthenticated_cannot_post(self, client):
        r = client.post("/api/posts", json={"song_name": "x", "artist": "y"})
        assert r.status_code in (401, 403)


class TestReactToTune:
    def _post_tune(self, client, token, suffix=""):
        """Helper to post a tune and return its id."""
        r = client.post("/api/posts",
                        json={"song_name": f"React Song {suffix}", "artist": "Artist"},
                        headers=auth_headers(token))
        return r.json()["id"]

    def test_like_tune(self, client):
        token_a = register_user(client, suffix="react1a")
        token_b = register_user(client, suffix="react1b")
        tune_id = self._post_tune(client, token_a, "a")
        r = client.post(f"/api/posts/{tune_id}/react",
                        json={"reaction_type": "like"},
                        headers=auth_headers(token_b))
        assert r.status_code == 200
        assert r.json()["likes"] == 1

    def test_dislike_tune(self, client):
        token_a = register_user(client, suffix="react2a")
        token_b = register_user(client, suffix="react2b")
        tune_id = self._post_tune(client, token_a, "b")
        r = client.post(f"/api/posts/{tune_id}/react",
                        json={"reaction_type": "dislike"},
                        headers=auth_headers(token_b))
        assert r.status_code == 200
        assert r.json()["dislikes"] == 1

    def test_toggle_off_same_reaction(self, client):
        token_a = register_user(client, suffix="react3a")
        token_b = register_user(client, suffix="react3b")
        tune_id = self._post_tune(client, token_a, "c")
        # Like once
        client.post(f"/api/posts/{tune_id}/react",
                    json={"reaction_type": "like"},
                    headers=auth_headers(token_b))
        # Like again → should toggle off
        r = client.post(f"/api/posts/{tune_id}/react",
                        json={"reaction_type": "like"},
                        headers=auth_headers(token_b))
        assert r.json()["likes"] == 0
        assert r.json()["my_reaction"] is None

    def test_switch_reaction(self, client):
        token_a = register_user(client, suffix="react4a")
        token_b = register_user(client, suffix="react4b")
        tune_id = self._post_tune(client, token_a, "d")
        # Like first
        client.post(f"/api/posts/{tune_id}/react",
                    json={"reaction_type": "like"},
                    headers=auth_headers(token_b))
        # Switch to dislike
        r = client.post(f"/api/posts/{tune_id}/react",
                        json={"reaction_type": "dislike"},
                        headers=auth_headers(token_b))
        assert r.json()["likes"] == 0
        assert r.json()["dislikes"] == 1
        assert r.json()["my_reaction"] == "dislike"

    def test_my_reaction_field(self, client):
        token_a = register_user(client, suffix="react5a")
        token_b = register_user(client, suffix="react5b")
        tune_id = self._post_tune(client, token_a, "e")
        r = client.post(f"/api/posts/{tune_id}/react",
                        json={"reaction_type": "like"},
                        headers=auth_headers(token_b))
        assert r.json()["my_reaction"] == "like"

    def test_react_nonexistent_tune(self, client):
        token = register_user(client, suffix="reactnone")
        r = client.post("/api/posts/99999/react",
                        json={"reaction_type": "like"},
                        headers=auth_headers(token))
        assert r.status_code == 404

    def test_unauthenticated_cannot_react(self, client):
        r = client.post("/api/posts/1/react", json={"reaction_type": "like"})
        assert r.status_code in (401, 403)


class TestDeleteTune:
    def test_owner_can_delete(self, client):
        token = register_user(client, suffix="del1")
        r = client.post("/api/posts",
                        json={"song_name": "Delete Me", "artist": "Artist"},
                        headers=auth_headers(token))
        tune_id = r.json()["id"]
        r2 = client.delete(f"/api/posts/{tune_id}", headers=auth_headers(token))
        assert r2.status_code == 200
        assert r2.json()["ok"] is True
        # Should be gone from feed
        posts = client.get("/api/posts", headers=auth_headers(token)).json()
        assert tune_id not in [p["id"] for p in posts]

    def test_non_owner_cannot_delete(self, client):
        token_a = register_user(client, suffix="del2a")
        token_b = register_user(client, suffix="del2b")
        r = client.post("/api/posts",
                        json={"song_name": "A's Song", "artist": "Artist"},
                        headers=auth_headers(token_a))
        tune_id = r.json()["id"]
        r2 = client.delete(f"/api/posts/{tune_id}", headers=auth_headers(token_b))
        assert r2.status_code == 404

    def test_delete_nonexistent_tune(self, client):
        token = register_user(client, suffix="del3")
        r = client.delete("/api/posts/99999", headers=auth_headers(token))
        assert r.status_code == 404
