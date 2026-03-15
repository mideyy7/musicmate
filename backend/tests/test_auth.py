"""Tests for /api/auth endpoints."""
import io
import pytest
from tests.conftest import auth_headers, register_user


class TestSSOInitiate:
    def test_valid_manchester_email(self, client):
        r = client.post("/api/auth/sso/initiate", json={"email": "john@student.manchester.ac.uk"})
        assert r.status_code == 200
        data = r.json()
        # SSO initiate returns: email, student_id, course, year, faculty
        assert "student_id" in data
        assert "course" in data
        assert "year" in data
        assert "faculty" in data

    def test_non_manchester_email_rejected(self, client):
        r = client.post("/api/auth/sso/initiate", json={"email": "user@gmail.com"})
        assert r.status_code == 403
        assert "Manchester" in r.json()["detail"]

    def test_duplicate_email_rejected(self, client):
        email = "dup@student.manchester.ac.uk"
        r = client.post("/api/auth/sso/initiate", json={"email": email})
        assert r.status_code == 200
        sso = r.json()
        client.post("/api/auth/sso/complete", json={
            "email": email,
            "password": "Pass123!",
            "display_name": "Dup User",
            "student_id": sso["student_id"],
            "course": sso["course"],
            "year": sso["year"],
            "faculty": sso["faculty"],
            "show_course": True,
            "show_year": True,
            "show_faculty": True,
        })
        # Initiate again for same (now registered) email
        r2 = client.post("/api/auth/sso/initiate", json={"email": email})
        assert r2.status_code == 409

    def test_manchester_ac_uk_domain_accepted(self, client):
        r = client.post("/api/auth/sso/initiate", json={"email": "staff@manchester.ac.uk"})
        assert r.status_code == 200


class TestSSOComplete:
    def test_creates_user_returns_token(self, client):
        email = "newuser@student.manchester.ac.uk"
        r = client.post("/api/auth/sso/initiate", json={"email": email})
        sso = r.json()
        r2 = client.post("/api/auth/sso/complete", json={
            "email": email,
            "password": "SecurePass1!",
            "display_name": "New User",
            "student_id": sso["student_id"],
            "course": sso["course"],
            "year": sso["year"],
            "faculty": sso["faculty"],
            "show_course": True,
            "show_year": True,
            "show_faculty": True,
        })
        assert r2.status_code == 200
        assert "access_token" in r2.json()

    def test_non_manchester_email_rejected(self, client):
        r = client.post("/api/auth/sso/complete", json={
            "email": "hack@evil.com",
            "password": "pass",
            "display_name": "Hacker",
            "student_id": "0",
            "course": "CS",
            "year": 1,
            "faculty": "Sci",
            "show_course": True,
            "show_year": True,
            "show_faculty": True,
        })
        assert r.status_code == 403

    def test_duplicate_registration_rejected(self, client):
        register_user(client, suffix="dup2")
        email = "testdup2@student.manchester.ac.uk"
        r = client.post("/api/auth/sso/complete", json={
            "email": email,
            "password": "pass",
            "display_name": "Dup",
            "student_id": "0",
            "course": "CS",
            "year": 1,
            "faculty": "Sci",
            "show_course": True,
            "show_year": True,
            "show_faculty": True,
        })
        assert r.status_code == 409


class TestLogin:
    def test_valid_credentials(self, client):
        register_user(client, suffix="logintest")
        r = client.post("/api/auth/login", json={
            "email": "testlogintest@student.manchester.ac.uk",
            "password": "TestPass123!",
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_wrong_password(self, client):
        register_user(client, suffix="loginwrong")
        r = client.post("/api/auth/login", json={
            "email": "testloginwrong@student.manchester.ac.uk",
            "password": "WrongPassword",
        })
        assert r.status_code == 401

    def test_unknown_email(self, client):
        r = client.post("/api/auth/login", json={
            "email": "nobody@student.manchester.ac.uk",
            "password": "pass",
        })
        assert r.status_code == 401


class TestGetMe:
    def test_returns_user_profile(self, client):
        token = register_user(client, suffix="metest")
        r = client.get("/api/auth/me", headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "testmetest@student.manchester.ac.uk"
        assert "display_name" in data
        assert "id" in data

    def test_unauthenticated_rejected(self, client):
        r = client.get("/api/auth/me")
        assert r.status_code in (401, 403)

    def test_invalid_token_rejected(self, client):
        r = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert r.status_code == 401


class TestUpdateMe:
    def test_update_bio(self, client):
        token = register_user(client, suffix="updatetest")
        r = client.put("/api/auth/me", json={"bio": "Love music!"}, headers=auth_headers(token))
        assert r.status_code == 200
        assert r.json()["bio"] == "Love music!"

    def test_update_multiple_fields(self, client):
        token = register_user(client, suffix="multiupdate")
        r = client.put("/api/auth/me", json={
            "nickname": "DJ Mike",
            "age": 21,
            "hobbies": "Guitar, Drums",
            "fun_fact": "I can beatbox",
        }, headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert data["nickname"] == "DJ Mike"
        assert data["age"] == 21
        assert data["hobbies"] == "Guitar, Drums"

    def test_empty_update_rejected(self, client):
        token = register_user(client, suffix="emptyupdate")
        r = client.put("/api/auth/me", json={}, headers=auth_headers(token))
        assert r.status_code == 400

    def test_privacy_settings_update(self, client):
        token = register_user(client, suffix="privacy")
        r = client.put("/api/auth/me", json={
            "show_course": False,
            "show_year": False,
            "show_faculty": True,
        }, headers=auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert data["show_course"] is False
        assert data["show_year"] is False


class TestUploadPicture:
    def test_upload_jpeg(self, client):
        token = register_user(client, suffix="pictest")
        fake_image = io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 14 + b"\xff\xd9")
        r = client.post(
            "/api/auth/me/picture",
            headers=auth_headers(token),
            files={"file": ("avatar.jpg", fake_image, "image/jpeg")},
        )
        assert r.status_code == 200
        pic = r.json()["profile_picture"]
        assert pic is not None
        assert "user_" in pic

    def test_upload_png(self, client):
        token = register_user(client, suffix="pngtest")
        fake_png = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        r = client.post(
            "/api/auth/me/picture",
            headers=auth_headers(token),
            files={"file": ("photo.png", fake_png, "image/png")},
        )
        assert r.status_code == 200
        assert r.json()["profile_picture"].endswith(".png")

    def test_upload_unauthenticated(self, client):
        fake_image = io.BytesIO(b"fake")
        r = client.post(
            "/api/auth/me/picture",
            files={"file": ("img.jpg", fake_image, "image/jpeg")},
        )
        assert r.status_code in (401, 403)
