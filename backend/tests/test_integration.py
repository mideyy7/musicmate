"""End-to-end integration tests simulating real user workflows."""
import pytest
from tests.conftest import auth_headers, register_user


class TestFullUserJourney:
    """Simulate the complete user journey from signup to chat."""

    def test_signup_sync_match_chat(self, client):
        # 1. Register two users
        token_a = register_user(client, suffix="e2ea")
        token_b = register_user(client, suffix="e2eb")

        # 2. Sync Spotify profiles
        sync_a = client.post("/api/spotify/sync", headers=auth_headers(token_a))
        sync_b = client.post("/api/spotify/sync", headers=auth_headers(token_b))
        assert sync_a.status_code == 200
        assert sync_b.status_code == 200

        # 3. Check Spotify status
        status_a = client.get("/api/spotify/status", headers=auth_headers(token_a))
        assert status_a.json()["connected"] is True

        # 4. Get match feed — B should appear
        feed = client.get("/api/match/feed", headers=auth_headers(token_a))
        assert feed.status_code == 200
        b_id = client.get("/api/auth/me", headers=auth_headers(token_b)).json()["id"]
        assert b_id in [c["user_id"] for c in feed.json()]

        # 5. Swipe — mock mode auto-reciprocates → instant match
        swipe = client.post("/api/match/swipe",
                            json={"target_user_id": b_id, "action": "like"},
                            headers=auth_headers(token_a))
        assert swipe.status_code == 200
        assert swipe.json()["is_match"] is True
        match_id = swipe.json()["match_id"]

        # 6. Confirm match in list
        matches = client.get("/api/match/matches", headers=auth_headers(token_a))
        match_ids = [m["id"] for m in matches.json()]
        assert match_id in match_ids

        # 7. Send messages
        msg1 = client.post(f"/api/chat/{match_id}",
                           json={"content": "Hey, I love your taste!", "message_type": "text"},
                           headers=auth_headers(token_a))
        assert msg1.status_code == 200

        msg2 = client.post(f"/api/chat/{match_id}",
                           json={"content": "Same here!", "message_type": "text"},
                           headers=auth_headers(token_b))
        assert msg2.status_code == 200

        # 8. Read messages
        convo = client.get(f"/api/chat/{match_id}", headers=auth_headers(token_a))
        assert len(convo.json()) == 2

        # 9. Mark messages as read
        read = client.put(f"/api/chat/{match_id}/read", headers=auth_headers(token_b))
        assert read.json()["marked_read"] >= 1

        # 10. Share a song
        song_msg = client.post(f"/api/chat/{match_id}", json={
            "content": "Check this out!",
            "message_type": "song_share",
            "song_data": {
                "track_name": "505",
                "artist": "Arctic Monkeys",
                "album": "Favourite Worst Nightmare",
                "spotify_id": "0BxE4FqsDD1Ot4YuBXwAPp",
            },
        }, headers=auth_headers(token_a))
        assert song_msg.status_code == 200
        assert song_msg.json()["song_data"]["track_name"] == "505"


class TestProfileUpdateFlow:
    def test_update_profile_then_see_in_match_feed(self, client):
        token_a = register_user(client, suffix="prof1a")
        token_b = register_user(client, suffix="prof1b")

        # Update A's profile
        client.put("/api/auth/me", json={
            "bio": "Big indie music fan",
            "age": 20,
            "hobbies": "Guitar, Concerts",
        }, headers=auth_headers(token_a))

        # Sync both
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        client.post("/api/spotify/sync", headers=auth_headers(token_b))

        # B looks at match feed — A should appear with bio
        feed = client.get("/api/match/feed", headers=auth_headers(token_b))
        a_id = client.get("/api/auth/me", headers=auth_headers(token_a)).json()["id"]
        candidates = {c["user_id"]: c for c in feed.json()}
        assert a_id in candidates
        assert candidates[a_id]["bio"] == "Big indie music fan"
        assert candidates[a_id]["age"] == 20


class TestDailyTunesFlow:
    def test_post_react_streak_flow(self, client):
        token_a = register_user(client, suffix="dt1a")
        token_b = register_user(client, suffix="dt1b")

        # A posts a tune
        post = client.post("/api/posts",
                           json={"song_name": "Heat Waves", "artist": "Glass Animals"},
                           headers=auth_headers(token_a))
        assert post.status_code == 200
        tune_id = post.json()["id"]

        # B likes A's tune
        like = client.post(f"/api/posts/{tune_id}/react",
                           json={"reaction_type": "like"},
                           headers=auth_headers(token_b))
        assert like.json()["likes"] == 1

        # A sees their tune has a like
        posts = client.get("/api/posts", headers=auth_headers(token_a)).json()
        target = next(p for p in posts if p["id"] == tune_id)
        assert target["likes"] == 1

        # A deletes their own tune
        delete = client.delete(f"/api/posts/{tune_id}", headers=auth_headers(token_a))
        assert delete.json()["ok"] is True


class TestCompatibilityScoring:
    def test_compatibility_score_between_users(self, client):
        token_a = register_user(client, suffix="cs1a")
        token_b = register_user(client, suffix="cs1b")
        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        client.post("/api/spotify/sync", headers=auth_headers(token_b))

        feed = client.get("/api/match/feed", headers=auth_headers(token_a))
        b_id = client.get("/api/auth/me", headers=auth_headers(token_b)).json()["id"]
        candidates = {c["user_id"]: c for c in feed.json()}

        if b_id in candidates:
            c = candidates[b_id]
            assert 0 <= c["compatibility_score"] <= 100
            assert isinstance(c["breakdown"]["shared_artists"], list)
            assert isinstance(c["breakdown"]["shared_genres"], list)
            assert 0 <= c["breakdown"]["genre_overlap_pct"] <= 100
            assert 0 <= c["breakdown"]["artist_overlap_pct"] <= 100


class TestPrivacySettings:
    def test_hidden_fields_not_in_feed(self, client):
        token_a = register_user(client, suffix="priv1a")
        token_b = register_user(client, suffix="priv1b")

        # A hides course and year
        client.put("/api/auth/me", json={
            "show_course": False,
            "show_year": False,
            "show_faculty": True,
        }, headers=auth_headers(token_a))

        client.post("/api/spotify/sync", headers=auth_headers(token_a))
        client.post("/api/spotify/sync", headers=auth_headers(token_b))

        feed = client.get("/api/match/feed", headers=auth_headers(token_b))
        a_id = client.get("/api/auth/me", headers=auth_headers(token_a)).json()["id"]
        candidates = {c["user_id"]: c for c in feed.json()}

        if a_id in candidates:
            assert candidates[a_id]["course"] is None
            assert candidates[a_id]["year"] is None
