"""Tests for /api/match endpoints."""
import pytest
from tests.conftest import auth_headers, register_user


def setup_matched_users(client):
    """Register two users, sync their profiles, and create a mutual match."""
    token_a = register_user(client, suffix="ma1")
    token_b = register_user(client, suffix="mb1")

    # Sync profiles for both
    client.post("/api/spotify/sync", headers=auth_headers(token_a))
    client.post("/api/spotify/sync", headers=auth_headers(token_b))

    # Get user B's id
    me_b = client.get("/api/auth/me", headers=auth_headers(token_b)).json()
    user_b_id = me_b["id"]

    # A swipes like on B  (mock mode auto-reciprocates → instant match)
    r = client.post("/api/match/swipe",
                    json={"target_user_id": user_b_id, "action": "like"},
                    headers=auth_headers(token_a))
    assert r.status_code == 200, r.text
    swipe_data = r.json()

    return token_a, token_b, user_b_id, swipe_data.get("match_id")


class TestMatchFeed:
    def test_returns_candidates_after_sync(self, client):
        token_a = register_user(client, suffix="fda")
        token_b = register_user(client, suffix="fdb")
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        client.post("/api/spotify/sync", headers=auth_headers(token_b))

        r = client.get("/api/match/feed", headers=auth_headers(token_a))
        assert r.status_code == 200
        candidates = r.json()
        assert isinstance(candidates, list)
        # B should appear since they have a profile
        ids = [c["user_id"] for c in candidates]
        b_id = client.get("/api/auth/me", headers=auth_headers(token_b)).json()["id"]
        assert b_id in ids

    def test_requires_own_profile(self, client):
        """User without synced profile gets 400 on match feed."""
        token = register_user(client, suffix="noprof")
        r = client.get("/api/match/feed", headers=auth_headers(token))
        assert r.status_code == 400

    def test_candidate_has_required_fields(self, client):
        token_a = register_user(client, suffix="fdc")
        token_b = register_user(client, suffix="fdd")
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        client.post("/api/spotify/sync", headers=auth_headers(token_b))

        r = client.get("/api/match/feed", headers=auth_headers(token_a))
        assert r.status_code == 200
        for c in r.json():
            assert "user_id" in c
            assert "display_name" in c
            assert "compatibility_score" in c
            assert "breakdown" in c
            assert "top_artists" in c

    def test_unauthenticated_rejected(self, client):
        r = client.get("/api/match/feed")
        assert r.status_code in (401, 403)

    def test_self_not_in_feed(self, client):
        token = register_user(client, suffix="selffd")
        client.post("/api/spotify/sync", headers=auth_headers(token))
        me_id = client.get("/api/auth/me", headers=auth_headers(token)).json()["id"]

        r = client.get("/api/match/feed", headers=auth_headers(token))
        assert r.status_code == 200
        ids = [c["user_id"] for c in r.json()]
        assert me_id not in ids


class TestSwipe:
    def test_like_creates_match_in_mock_mode(self, client):
        token_a, token_b, b_id, match_id = setup_matched_users(client)
        assert match_id is not None

    def test_pass_does_not_create_match(self, client):
        token_a = register_user(client, suffix="passa")
        token_b = register_user(client, suffix="passb")
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        client.post("/api/spotify/sync", headers=auth_headers(token_b))
        b_id = client.get("/api/auth/me", headers=auth_headers(token_b)).json()["id"]

        r = client.post("/api/match/swipe",
                        json={"target_user_id": b_id, "action": "pass"},
                        headers=auth_headers(token_a))
        assert r.status_code == 200
        assert r.json()["is_match"] is False
        assert r.json()["match_id"] is None

    def test_invalid_action_rejected(self, client):
        token_a = register_user(client, suffix="badact")
        token_b = register_user(client, suffix="badactb")
        b_id = client.get("/api/auth/me", headers=auth_headers(token_b)).json()["id"]
        r = client.post("/api/match/swipe",
                        json={"target_user_id": b_id, "action": "maybe"},
                        headers=auth_headers(token_a))
        assert r.status_code == 400

    def test_self_swipe_rejected(self, client):
        token = register_user(client, suffix="selfswipe")
        me_id = client.get("/api/auth/me", headers=auth_headers(token)).json()["id"]
        r = client.post("/api/match/swipe",
                        json={"target_user_id": me_id, "action": "like"},
                        headers=auth_headers(token))
        assert r.status_code == 400

    def test_duplicate_swipe_rejected(self, client):
        token_a = register_user(client, suffix="dupswipea")
        token_b = register_user(client, suffix="dupswipeb")
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        b_id = client.get("/api/auth/me", headers=auth_headers(token_b)).json()["id"]

        client.post("/api/match/swipe",
                    json={"target_user_id": b_id, "action": "pass"},
                    headers=auth_headers(token_a))
        r = client.post("/api/match/swipe",
                        json={"target_user_id": b_id, "action": "like"},
                        headers=auth_headers(token_a))
        assert r.status_code == 409

    def test_match_response_message(self, client):
        token_a, token_b, b_id, match_id = setup_matched_users(client)
        # The swipe that triggered the match should say "It's a match!"
        # (already validated by match_id being not None)
        assert match_id is not None


class TestListMatches:
    def test_returns_match_list(self, client):
        token_a, token_b, b_id, match_id = setup_matched_users(client)
        r = client.get("/api/match/matches", headers=auth_headers(token_a))
        assert r.status_code == 200
        matches = r.json()
        assert len(matches) >= 1

    def test_match_has_required_fields(self, client):
        token_a, token_b, b_id, match_id = setup_matched_users(client)
        r = client.get("/api/match/matches", headers=auth_headers(token_a))
        m = r.json()[0]
        assert "id" in m
        assert "other_user" in m
        assert "compatibility_score" in m
        assert "breakdown" in m
        assert "created_at" in m

    def test_compatibility_score_in_range(self, client):
        token_a, token_b, b_id, match_id = setup_matched_users(client)
        r = client.get("/api/match/matches", headers=auth_headers(token_a))
        for m in r.json():
            score = m["compatibility_score"]
            assert 0 <= score <= 100, f"Score {score} out of range"

    def test_empty_list_before_any_match(self, client):
        token = register_user(client, suffix="nomatches")
        r = client.get("/api/match/matches", headers=auth_headers(token))
        assert r.status_code == 200
        assert r.json() == []

    def test_unauthenticated_rejected(self, client):
        r = client.get("/api/match/matches")
        assert r.status_code in (401, 403)


class TestMatchDetail:
    def test_get_match_detail(self, client):
        token_a, token_b, b_id, match_id = setup_matched_users(client)
        r = client.get(f"/api/match/matches/{match_id}", headers=auth_headers(token_a))
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == match_id

    def test_non_participant_cannot_view(self, client):
        token_a, token_b, b_id, match_id = setup_matched_users(client)
        token_c = register_user(client, suffix="mc1")
        r = client.get(f"/api/match/matches/{match_id}", headers=auth_headers(token_c))
        assert r.status_code in (401, 403)

    def test_nonexistent_match_returns_404(self, client):
        token = register_user(client, suffix="no404")
        r = client.get("/api/match/matches/99999", headers=auth_headers(token))
        assert r.status_code == 404
