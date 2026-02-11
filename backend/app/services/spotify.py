import urllib.parse
from collections import Counter
from datetime import datetime, timedelta

import httpx

from app.core.config import settings

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

SCOPES = "user-top-read user-read-recently-played user-read-playback-state user-library-read"


def get_auth_url(state: str = "") -> str:
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": SCOPES,
        "show_dialog": "true",
    }
    if state:
        params["state"] = state
    return f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code(code: str) -> dict:
    """Exchange authorization code for access and refresh tokens."""
    response = httpx.post(
        SPOTIFY_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        },
        auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
    )
    response.raise_for_status()
    data = response.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": datetime.utcnow() + timedelta(seconds=data["expires_in"]),
    }


def refresh_access_token(refresh_token: str) -> dict:
    """Refresh an expired access token."""
    response = httpx.post(
        SPOTIFY_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
    )
    response.raise_for_status()
    data = response.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", refresh_token),
        "expires_at": datetime.utcnow() + timedelta(seconds=data["expires_in"]),
    }


def get_spotify_user_id(access_token: str) -> str:
    """Get the Spotify user's profile ID."""
    response = httpx.get(
        f"{SPOTIFY_API_BASE}/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json().get("id", "")


def fetch_top_artists(access_token: str, limit: int = 20, time_range: str = "medium_term") -> list[dict]:
    """Fetch user's top artists from Spotify."""
    response = httpx.get(
        f"{SPOTIFY_API_BASE}/me/top/artists",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": limit, "time_range": time_range},
    )
    response.raise_for_status()
    items = response.json().get("items", [])

    return [
        {
            "name": artist["name"],
            "spotify_id": artist["id"],
            "genres": artist.get("genres", []),
            "image_url": artist["images"][0]["url"] if artist.get("images") else None,
            "rank": i + 1,
        }
        for i, artist in enumerate(items)
    ]


def fetch_top_tracks(access_token: str, limit: int = 20, time_range: str = "medium_term") -> list[dict]:
    """Fetch user's top tracks from Spotify."""
    response = httpx.get(
        f"{SPOTIFY_API_BASE}/me/top/tracks",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": limit, "time_range": time_range},
    )
    response.raise_for_status()
    items = response.json().get("items", [])

    return [
        {
            "name": track["name"],
            "artist": ", ".join(a["name"] for a in track["artists"]),
            "album": track["album"]["name"],
            "image_url": track["album"]["images"][0]["url"] if track["album"].get("images") else None,
            "spotify_id": track["id"],
        }
        for track in items
    ]


def fetch_recent_tracks(access_token: str, limit: int = 20) -> list[dict]:
    """Fetch user's recently played tracks from Spotify."""
    response = httpx.get(
        f"{SPOTIFY_API_BASE}/me/player/recently-played",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": limit},
    )
    response.raise_for_status()
    items = response.json().get("items", [])

    return [
        {
            "name": item["track"]["name"],
            "artist": ", ".join(a["name"] for a in item["track"]["artists"]),
            "album": item["track"]["album"]["name"],
            "image_url": (
                item["track"]["album"]["images"][0]["url"]
                if item["track"]["album"].get("images")
                else None
            ),
            "played_at": item.get("played_at"),
            "spotify_id": item["track"]["id"],
        }
        for item in items
    ]


def build_music_profile(top_artists: list[dict], top_tracks: list[dict], recent_tracks: list[dict]) -> dict:
    """Process raw Spotify data into a structured music profile."""
    genre_counter = Counter()
    for artist in top_artists:
        for genre in artist.get("genres", []):
            genre_counter[genre] += 1

    top_genres = [
        {"genre": genre, "count": count}
        for genre, count in genre_counter.most_common(15)
    ]

    listening_patterns = {
        "total_artists": len(top_artists),
        "total_genres": len(genre_counter),
        "top_genre": top_genres[0]["genre"] if top_genres else None,
        "avg_popularity": 0,
    }

    return {
        "top_artists": top_artists,
        "top_genres": top_genres,
        "recent_tracks": recent_tracks,
        "listening_patterns": listening_patterns,
    }
