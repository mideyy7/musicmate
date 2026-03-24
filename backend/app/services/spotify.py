import random
import urllib.parse
from collections import Counter
from datetime import datetime, timedelta

import httpx

from app.core.config import settings


def is_mock_mode() -> bool:
    if settings.FORCE_MOCK_MODE:
        return True
    return not settings.SPOTIFY_CLIENT_ID or settings.SPOTIFY_CLIENT_ID == "your_spotify_client_id_here"


# Pool of mock data for generating realistic gospel music profiles
MOCK_ARTISTS_POOL = [
    {"name": "Kirk Franklin",         "spotify_id": "2hGh5DVzdDMEkGiqnzYuNP", "genres": ["gospel", "urban gospel", "contemporary gospel"],       "image_url": "https://i.pravatar.cc/150?u=kirkfranklin"},
    {"name": "Tasha Cobbs Leonard",   "spotify_id": "7oPgCQqMMXEXrNau5vxYZP", "genres": ["gospel", "contemporary gospel", "praise and worship"],  "image_url": "https://i.pravatar.cc/150?u=tashacobbs"},
    {"name": "Travis Greene",         "spotify_id": "1HEvB0GRgBDMTU3oHbJXVA", "genres": ["gospel", "contemporary gospel", "praise and worship"],  "image_url": "https://i.pravatar.cc/150?u=travisgreene"},
    {"name": "Maverick City Music",   "spotify_id": "5K4W6rqBFWDnAN6FQUkS6x", "genres": ["gospel", "contemporary worship", "ccm"],               "image_url": "https://i.pravatar.cc/150?u=maverickcity"},
    {"name": "Elevation Worship",     "spotify_id": "6l4IkSGBVB3RxgxPNSCBm0", "genres": ["contemporary worship", "ccm", "praise and worship"],   "image_url": "https://i.pravatar.cc/150?u=elevationworship"},
    {"name": "Hillsong Worship",      "spotify_id": "55jKRr1LhRGDhzJNRmCgjq", "genres": ["contemporary worship", "ccm", "praise and worship"],   "image_url": "https://i.pravatar.cc/150?u=hillsongworship"},
    {"name": "Hillsong United",       "spotify_id": "6Ap4Uz1ur6vDqzl0KBLGPL", "genres": ["contemporary worship", "ccm", "praise and worship"],   "image_url": "https://i.pravatar.cc/150?u=hillsongunited"},
    {"name": "CeCe Winans",           "spotify_id": "2kkuP6gVHBvbJIonjJGvnJ", "genres": ["gospel", "traditional gospel", "contemporary gospel"], "image_url": "https://i.pravatar.cc/150?u=cecewinans"},
    {"name": "Donnie McClurkin",      "spotify_id": "0YrxMnMvR1jFsv0AxoRnAS", "genres": ["gospel", "traditional gospel", "urban gospel"],        "image_url": "https://i.pravatar.cc/150?u=donniemcclurkin"},
    {"name": "Fred Hammond",          "spotify_id": "48OEcGpnWWLCVGHToQk9lK", "genres": ["gospel", "urban gospel", "traditional gospel"],        "image_url": "https://i.pravatar.cc/150?u=fredhammond"},
    {"name": "Yolanda Adams",         "spotify_id": "0KSb7YvdSrGjhXGmkiELd7", "genres": ["gospel", "contemporary gospel", "urban gospel"],       "image_url": "https://i.pravatar.cc/150?u=yolandaadams"},
    {"name": "Jonathan McReynolds",   "spotify_id": "4EiDKEbKSMSBONsRBdCssP", "genres": ["gospel", "contemporary gospel", "urban gospel"],       "image_url": "https://i.pravatar.cc/150?u=jonathanmcreynolds"},
    {"name": "Chandler Moore",        "spotify_id": "6VuMaDnrHyPlt7yPLFVAZI", "genres": ["gospel", "contemporary worship", "ccm"],               "image_url": "https://i.pravatar.cc/150?u=chandlermoore"},
    {"name": "Sinach",                "spotify_id": "0kqnO5pI78JOiHXUoI1JGM", "genres": ["gospel", "african gospel", "praise and worship"],      "image_url": "https://i.pravatar.cc/150?u=sinach"},
    {"name": "Dunsin Oyekan",         "spotify_id": "5g7JkGFZjBGUqSEBnnlCaF", "genres": ["gospel", "african gospel", "nigerian gospel"],         "image_url": "https://i.pravatar.cc/150?u=dunsinoyekan"},
    {"name": "Theophilus Sunday",     "spotify_id": "6TIYQ3jFPwQSRmorE2soZN", "genres": ["gospel", "nigerian gospel", "african gospel"],         "image_url": "https://i.pravatar.cc/150?u=theophilussunday"},
    {"name": "Phil Thompson",         "spotify_id": "5rVpDTR5n2dRdxAnOiOaU5", "genres": ["gospel", "contemporary gospel", "urban gospel"],       "image_url": "https://i.pravatar.cc/150?u=philthompson"},
    {"name": "Dante Bowe",            "spotify_id": "2RdwBSPQiwcmiDo9sly8ds", "genres": ["gospel", "contemporary worship", "ccm"],               "image_url": "https://i.pravatar.cc/150?u=dantebowe"},
    {"name": "Lauren Daigle",         "spotify_id": "5zzMfACEjzuAFdQAoE4UJQ", "genres": ["contemporary christian", "ccm", "pop gospel"],         "image_url": "https://i.pravatar.cc/150?u=laurendaigle"},
    {"name": "Cory Asbury",           "spotify_id": "5m8H0EqlboTEkFdFcCQieP", "genres": ["contemporary worship", "ccm", "praise and worship"],   "image_url": "https://i.pravatar.cc/150?u=coryasbury"},
]

MOCK_TRACKS_POOL = [
    {"name": "Way Maker",                "artist": "Sinach",              "album": "Way Maker",           "spotify_id": "g1"},
    {"name": "The Blessing",             "artist": "Elevation Worship",   "album": "Graves Into Gardens", "spotify_id": "g2"},
    {"name": "Goodness of God",          "artist": "CeCe Winans",         "album": "Believe For It",      "spotify_id": "g3"},
    {"name": "What A Beautiful Name",    "artist": "Hillsong Worship",    "album": "Let There Be Light",  "spotify_id": "g4"},
    {"name": "Joyful",                   "artist": "Dante Bowe",          "album": "Circles",             "spotify_id": "g5"},
    {"name": "Reckless Love",            "artist": "Cory Asbury",         "album": "Reckless Love",       "spotify_id": "g6"},
    {"name": "Do It Again",              "artist": "Elevation Worship",   "album": "There Is a Cloud",    "spotify_id": "g7"},
    {"name": "Oceans",                   "artist": "Hillsong United",     "album": "Zion",                "spotify_id": "g8"},
    {"name": "Never Lost",               "artist": "Elevation Worship",   "album": "Graves Into Gardens", "spotify_id": "g9"},
    {"name": "You Know My Name",         "artist": "Tasha Cobbs Leonard", "album": "Heart. Passion. Pursuit.", "spotify_id": "g10"},
    {"name": "Jireh",                    "artist": "Maverick City Music", "album": "Jubilee: Juneteenth Edition", "spotify_id": "g11"},
    {"name": "Made a Way",               "artist": "Travis Greene",       "album": "Stretching Out",      "spotify_id": "g12"},
    {"name": "Holy Forever",             "artist": "Bethel Music",        "album": "Revival's In The Air","spotify_id": "g13"},
    {"name": "Talking to Jesus",         "artist": "Elevation Worship",   "album": "Lion",                "spotify_id": "g14"},
    {"name": "Fear Is Not My Future",    "artist": "Kirk Franklin",       "album": "Father's Day",        "spotify_id": "g15"},
]


def generate_mock_profile(user_id: int) -> dict:
    """Generate a deterministic but varied mock music profile based on user_id."""
    rng = random.Random(user_id)
    num_artists = rng.randint(8, 15)
    artists = rng.sample(MOCK_ARTISTS_POOL, min(num_artists, len(MOCK_ARTISTS_POOL)))
    top_artists = [
        {**a, "rank": i + 1}  # image_url comes from MOCK_ARTISTS_POOL entry
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

SCOPES = "user-top-read user-read-recently-played user-read-playback-state user-library-read user-library-modify playlist-modify-public playlist-modify-private streaming user-modify-playback-state"


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
            "spotify_url": track["external_urls"].get("spotify"),
            "preview_url": track.get("preview_url"),
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
            "spotify_url": item["track"]["external_urls"].get("spotify"),
            "preview_url": item["track"].get("preview_url"),
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


# --- Search ---

def search_tracks(access_token: str, query: str, limit: int = 10) -> list[dict]:
    """Search Spotify for tracks matching a query."""
    response = httpx.get(
        f"{SPOTIFY_API_BASE}/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query, "type": "track", "limit": limit},
    )
    response.raise_for_status()
    items = response.json().get("tracks", {}).get("items", [])
    return [
        {
            "track_name": track["name"],
            "artist": ", ".join(a["name"] for a in track["artists"]),
            "album": track["album"]["name"],
            "image_url": track["album"]["images"][0]["url"] if track["album"].get("images") else None,
            "spotify_id": track["id"],
            "spotify_url": track["external_urls"].get("spotify"),
            "preview_url": track.get("preview_url"),
        }
        for track in items
    ]


def save_track_to_library(access_token: str, track_id: str) -> bool:
    """Save a track to the user's Spotify Liked Songs."""
    response = httpx.put(
        f"{SPOTIFY_API_BASE}/me/tracks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"ids": [track_id]},
    )
    response.raise_for_status()
    return True


# --- Playlist functions ---

def create_spotify_playlist(access_token: str, user_spotify_id: str, name: str, description: str = "") -> str:
    """Create a playlist on Spotify. Returns the playlist ID."""
    if is_mock_mode():
        return f"mock_playlist_{name.replace(' ', '_').lower()}"

    response = httpx.post(
        f"{SPOTIFY_API_BASE}/users/{user_spotify_id}/playlists",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": name, "description": description, "public": False},
    )
    response.raise_for_status()
    return response.json()["id"]


def add_tracks_to_spotify_playlist(access_token: str, playlist_id: str, track_uris: list[str]) -> bool:
    """Add tracks to a Spotify playlist."""
    if is_mock_mode():
        return True

    response = httpx.post(
        f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"uris": track_uris},
    )
    response.raise_for_status()
    return True


def remove_tracks_from_spotify_playlist(access_token: str, playlist_id: str, track_uris: list[str]) -> bool:
    """Remove tracks from a Spotify playlist."""
    if is_mock_mode():
        return True

    response = httpx.request(
        "DELETE",
        f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"tracks": [{"uri": uri} for uri in track_uris]},
    )
    response.raise_for_status()
    return True
