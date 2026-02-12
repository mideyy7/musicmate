import random
import urllib.parse
from collections import Counter
from datetime import datetime, timedelta

import httpx

from app.core.config import settings


def is_mock_mode() -> bool:
    return not settings.SPOTIFY_CLIENT_ID or settings.SPOTIFY_CLIENT_ID == "your_spotify_client_id_here"


# Pool of mock data for generating realistic profiles
MOCK_ARTISTS_POOL = [
    {"name": "Arctic Monkeys", "spotify_id": "7Ln80lUS6He07XvHI8qqHH", "genres": ["indie rock", "rock", "sheffield indie"]},
    {"name": "Tame Impala", "spotify_id": "5INjqkS1o8h1imAzPqGZBb", "genres": ["psychedelic rock", "indie rock", "neo-psychedelia"]},
    {"name": "Kendrick Lamar", "spotify_id": "2YZyLoL8N0Wb9xBt1NhZWg", "genres": ["hip hop", "rap", "west coast rap"]},
    {"name": "Doja Cat", "spotify_id": "5cj0lLjcoR7YOSnhnX0Po5", "genres": ["pop", "dance pop", "rap"]},
    {"name": "The Weeknd", "spotify_id": "1Xyo4u8uXC1ZmMpatF05PJ", "genres": ["r&b", "pop", "canadian pop"]},
    {"name": "Tyler, The Creator", "spotify_id": "4V8LLVI7PbaPR0K2TGSxFF", "genres": ["hip hop", "rap", "alternative hip hop"]},
    {"name": "Frank Ocean", "spotify_id": "2h93pZq0e7k5yf4dywlkpM", "genres": ["r&b", "alternative r&b", "neo soul"]},
    {"name": "SZA", "spotify_id": "7tYKF4w9nC0nq9CsPZTHyP", "genres": ["r&b", "pop", "alternative r&b"]},
    {"name": "Radiohead", "spotify_id": "4Z8W4fKeB5YxbusRsdQVPb", "genres": ["alternative rock", "art rock", "electronic"]},
    {"name": "Steve Lacy", "spotify_id": "57vWImR43h4CaDao012Ofp", "genres": ["r&b", "indie soul", "bedroom pop"]},
    {"name": "Billie Eilish", "spotify_id": "6qqNVTkY8uBg9cP3Jd7DAH", "genres": ["pop", "electropop", "art pop"]},
    {"name": "Mac DeMarco", "spotify_id": "3Sz7ZnJQBIHsXLUSo0OQtM", "genres": ["indie rock", "lo-fi", "slacker rock"]},
    {"name": "Playboi Carti", "spotify_id": "699OTQXzgjhIYAHMy9RyPD", "genres": ["hip hop", "rap", "trap"]},
    {"name": "Dua Lipa", "spotify_id": "6M2wZ9GZgrQXHCFfjv46we", "genres": ["pop", "dance pop", "uk pop"]},
    {"name": "Travis Scott", "spotify_id": "0Y5tJX1MQlPlqiwlOH1tJY", "genres": ["hip hop", "rap", "trap"]},
    {"name": "Phoebe Bridgers", "spotify_id": "1r1uxoy19fzMxunt3ONAkG", "genres": ["indie rock", "indie folk", "singer-songwriter"]},
    {"name": "Daniel Caesar", "spotify_id": "20wkVLutqVOYrc0kxFs7rA", "genres": ["r&b", "canadian r&b", "neo soul"]},
    {"name": "Lana Del Rey", "spotify_id": "00FQb4jTyendYWaN8pK0wa", "genres": ["art pop", "indie pop", "baroque pop"]},
    {"name": "Bad Bunny", "spotify_id": "4q3ewBCX7sLwd24euuV69X", "genres": ["reggaeton", "latin trap", "latin pop"]},
    {"name": "Mitski", "spotify_id": "2uYWgrBGLiGKrpDbBDM2Pr", "genres": ["indie rock", "art pop", "indie pop"]},
]

MOCK_TRACKS_POOL = [
    {"name": "Do I Wanna Know?", "artist": "Arctic Monkeys", "album": "AM", "spotify_id": "m1"},
    {"name": "The Less I Know The Better", "artist": "Tame Impala", "album": "Currents", "spotify_id": "m2"},
    {"name": "HUMBLE.", "artist": "Kendrick Lamar", "album": "DAMN.", "spotify_id": "m3"},
    {"name": "Say So", "artist": "Doja Cat", "album": "Hot Pink", "spotify_id": "m4"},
    {"name": "Blinding Lights", "artist": "The Weeknd", "album": "After Hours", "spotify_id": "m5"},
    {"name": "EARFQUAKE", "artist": "Tyler, The Creator", "album": "IGOR", "spotify_id": "m6"},
    {"name": "Nights", "artist": "Frank Ocean", "album": "Blonde", "spotify_id": "m7"},
    {"name": "Kill Bill", "artist": "SZA", "album": "SOS", "spotify_id": "m8"},
    {"name": "Creep", "artist": "Radiohead", "album": "Pablo Honey", "spotify_id": "m9"},
    {"name": "Bad Habit", "artist": "Steve Lacy", "album": "Gemini Rights", "spotify_id": "m10"},
    {"name": "lovely", "artist": "Billie Eilish", "album": "WHEN WE ALL FALL ASLEEP", "spotify_id": "m11"},
    {"name": "Chamber of Reflection", "artist": "Mac DeMarco", "album": "Salad Days", "spotify_id": "m12"},
    {"name": "Magnolia", "artist": "Playboi Carti", "album": "Playboi Carti", "spotify_id": "m13"},
    {"name": "Levitating", "artist": "Dua Lipa", "album": "Future Nostalgia", "spotify_id": "m14"},
    {"name": "SICKO MODE", "artist": "Travis Scott", "album": "Astroworld", "spotify_id": "m15"},
]


def generate_mock_profile(user_id: int) -> dict:
    """Generate a deterministic but varied mock music profile based on user_id."""
    rng = random.Random(user_id)
    num_artists = rng.randint(8, 15)
    artists = rng.sample(MOCK_ARTISTS_POOL, min(num_artists, len(MOCK_ARTISTS_POOL)))
    top_artists = [
        {**a, "image_url": None, "rank": i + 1}
        for i, a in enumerate(artists)
    ]

    num_tracks = rng.randint(6, 12)
    tracks = rng.sample(MOCK_TRACKS_POOL, min(num_tracks, len(MOCK_TRACKS_POOL)))
    recent_tracks = [
        {**t, "image_url": None, "played_at": None}
        for t in tracks
    ]

    return build_music_profile(top_artists, tracks, recent_tracks)

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
