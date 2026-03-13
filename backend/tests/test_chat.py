"""Tests for /api/chat endpoints."""
import pytest
from tests.conftest import auth_headers, register_user


def create_match(client):
    """Helper: create two users + a mutual match. Returns (token_a, token_b, match_id)."""
    token_a = register_user(client, suffix="cha")
    token_b = register_user(client, suffix="chb")
    client.post("/api/spotify/sync", headers=auth_headers(token_a))
    client.post("/api/spotify/sync", headers=auth_headers(token_b))
    b_id = client.get("/api/auth/me", headers=auth_headers(token_b)).json()["id"]
    r = client.post("/api/match/swipe",
                    json={"target_user_id": b_id, "action": "like"},
                    headers=auth_headers(token_a))
    assert r.status_code == 200, r.text
    match_id = r.json()["match_id"]
    assert match_id is not None
    return token_a, token_b, match_id


class TestGetConversation:
    def test_empty_conversation(self, client):
        token_a, token_b, match_id = create_match(client)
        r = client.get(f"/api/chat/{match_id}", headers=auth_headers(token_a))
        assert r.status_code == 200
        assert r.json() == []

    def test_non_participant_cannot_read(self, client):
        token_a, token_b, match_id = create_match(client)
        token_c = register_user(client, suffix="chc")
        r = client.get(f"/api/chat/{match_id}", headers=auth_headers(token_c))
        assert r.status_code in (401, 403)

    def test_nonexistent_match_404(self, client):
        token = register_user(client, suffix="chd")
        r = client.get("/api/chat/99999", headers=auth_headers(token))
        assert r.status_code == 404

    def test_unauthenticated_rejected(self, client):
        r = client.get("/api/chat/1")
        assert r.status_code in (401, 403)


class TestSendMessage:
    def test_send_text_message(self, client):
        token_a, token_b, match_id = create_match(client)
        r = client.post(f"/api/chat/{match_id}",
                        json={"content": "Hello!", "message_type": "text"},
                        headers=auth_headers(token_a))
        assert r.status_code == 200
        data = r.json()
        assert data["content"] == "Hello!"
        assert data["message_type"] == "text"

    def test_message_appears_in_conversation(self, client):
        token_a, token_b, match_id = create_match(client)
        client.post(f"/api/chat/{match_id}",
                    json={"content": "Hey there", "message_type": "text"},
                    headers=auth_headers(token_a))
        r = client.get(f"/api/chat/{match_id}", headers=auth_headers(token_a))
        messages = r.json()
        assert len(messages) == 1
        assert messages[0]["content"] == "Hey there"

    def test_both_users_can_message(self, client):
        token_a, token_b, match_id = create_match(client)
        client.post(f"/api/chat/{match_id}",
                    json={"content": "From A", "message_type": "text"},
                    headers=auth_headers(token_a))
        client.post(f"/api/chat/{match_id}",
                    json={"content": "From B", "message_type": "text"},
                    headers=auth_headers(token_b))
        r = client.get(f"/api/chat/{match_id}", headers=auth_headers(token_a))
        assert len(r.json()) == 2

    def test_send_song_share(self, client):
        token_a, token_b, match_id = create_match(client)
        r = client.post(f"/api/chat/{match_id}", json={
            "content": "Check this out!",
            "message_type": "song_share",
            "song_data": {
                "track_name": "Blinding Lights",
                "artist": "The Weeknd",
                "album": "After Hours",
                "spotify_id": "0abc123",
            },
        }, headers=auth_headers(token_a))
        assert r.status_code == 200
        assert r.json()["message_type"] == "song_share"
        assert r.json()["song_data"] is not None

    def test_song_share_without_song_data_rejected(self, client):
        token_a, token_b, match_id = create_match(client)
        r = client.post(f"/api/chat/{match_id}",
                        json={"content": "song", "message_type": "song_share"},
                        headers=auth_headers(token_a))
        assert r.status_code == 400

    def test_invalid_message_type_rejected(self, client):
        token_a, token_b, match_id = create_match(client)
        r = client.post(f"/api/chat/{match_id}",
                        json={"content": "hi", "message_type": "sticker"},
                        headers=auth_headers(token_a))
        assert r.status_code == 400

    def test_outsider_cannot_send(self, client):
        token_a, token_b, match_id = create_match(client)
        token_c = register_user(client, suffix="che")
        r = client.post(f"/api/chat/{match_id}",
                        json={"content": "intrude", "message_type": "text"},
                        headers=auth_headers(token_c))
        assert r.status_code in (401, 403)


class TestMarkRead:
    def test_mark_messages_read(self, client):
        token_a, token_b, match_id = create_match(client)
        # A sends two messages
        for txt in ["msg1", "msg2"]:
            client.post(f"/api/chat/{match_id}",
                        json={"content": txt, "message_type": "text"},
                        headers=auth_headers(token_a))
        # B marks them as read
        r = client.put(f"/api/chat/{match_id}/read", headers=auth_headers(token_b))
        assert r.status_code == 200
        assert r.json()["marked_read"] == 2


class TestUnreadCount:
    def test_unread_count_increases(self, client):
        token_a, token_b, match_id = create_match(client)
        # A sends a message; B should have 1 unread
        client.post(f"/api/chat/{match_id}",
                    json={"content": "hi", "message_type": "text"},
                    headers=auth_headers(token_a))
        r = client.get("/api/chat/unread/count", headers=auth_headers(token_b))
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1

    def test_zero_unread_initially(self, client):
        token = register_user(client, suffix="zeroread")
        r = client.get("/api/chat/unread/count", headers=auth_headers(token))
        assert r.status_code == 200
        assert r.json()["total"] == 0


class TestChatUtilities:
    def test_prompts_list(self, client):
        r = client.get("/api/chat/prompts/list")
        assert r.status_code == 200
        prompts = r.json()["prompts"]
        assert isinstance(prompts, list)
        assert len(prompts) > 0

    def test_song_search_returns_results(self, client):
        token = register_user(client, suffix="songsearch")
        r = client.get("/api/chat/search-song/results?q=light", headers=auth_headers(token))
        assert r.status_code == 200
        results = r.json()
        assert isinstance(results, list)
        # "Blinding Lights" should match
        names = [res["track_name"] for res in results]
        assert any("light" in n.lower() for n in names)

    def test_song_search_no_results(self, client):
        token = register_user(client, suffix="songsearch2")
        r = client.get("/api/chat/search-song/results?q=xyzzznotarealsongtitle", headers=auth_headers(token))
        assert r.status_code == 200
        assert r.json() == []

    def test_song_search_requires_auth(self, client):
        r = client.get("/api/chat/search-song/results?q=love")
        assert r.status_code in (401, 403)
