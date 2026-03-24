from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from datetime import datetime, timedelta

from app.api.deps import get_current_user, get_db
from app.crud.match import get_match_by_id, get_matches
from app.crud.message import create_message, get_messages, get_unread_count, mark_messages_read
from app.crud.spotify import get_spotify_tokens, save_spotify_tokens
from app.models.user import User
from app.schemas.message import (
    MessageResponse,
    SendMessageRequest,
    SongSearchResult,
    UnreadCountResponse,
)
from app.services.spotify import is_mock_mode, refresh_access_token, search_tracks

router = APIRouter(prefix="/api/chat", tags=["chat"])

CONVERSATION_PROMPTS = [
    "What song has been stuck in your head lately?",
    "If you could only listen to one album forever, which would it be?",
    "What's a guilty pleasure song you secretly love?",
    "What was the first concert you ever went to?",
    "What genre do you listen to that might surprise people?",
    "What artist do you think is underrated?",
    "What song makes you feel nostalgic?",
    "Do you prefer live music or studio recordings?",
]

MOCK_SONG_RESULTS = [
    {"track_name": "Way Maker",             "artist": "Sinach",              "album": "Way Maker",                    "image_url": None, "spotify_url": "https://open.spotify.com/search/Way%20Maker%20Sinach",              "spotify_id": "6y0igZArWVi6Iz0rj35c1Y"},
    {"track_name": "The Blessing",          "artist": "Elevation Worship",   "album": "Graves Into Gardens",          "image_url": None, "spotify_url": "https://open.spotify.com/search/The%20Blessing%20Elevation%20Worship", "spotify_id": "3Blp2bAlBcxp8CBPF0T8W7"},
    {"track_name": "Goodness of God",       "artist": "CeCe Winans",         "album": "Believe For It",               "image_url": None, "spotify_url": "https://open.spotify.com/search/Goodness%20of%20God%20CeCe%20Winans",  "spotify_id": "1xR3kzx9OHTQP6UPKfSQfz"},
    {"track_name": "What A Beautiful Name", "artist": "Hillsong Worship",    "album": "Let There Be Light",           "image_url": None, "spotify_url": "https://open.spotify.com/search/What%20A%20Beautiful%20Name%20Hillsong","spotify_id": "0BjC1NfoEOOusryehmNe5R"},
    {"track_name": "Joyful",                "artist": "Dante Bowe",          "album": "Circles",                      "image_url": None, "spotify_url": "https://open.spotify.com/search/Joyful%20Dante%20Bowe",               "spotify_id": "0MoSqJpK8mglxq5W7YsJmj"},
    {"track_name": "Reckless Love",         "artist": "Cory Asbury",         "album": "Reckless Love",                "image_url": None, "spotify_url": "https://open.spotify.com/search/Reckless%20Love%20Cory%20Asbury",     "spotify_id": "1ZiP6JjWZCzFQvKNiOuvAi"},
    {"track_name": "Do It Again",           "artist": "Elevation Worship",   "album": "There Is a Cloud",             "image_url": None, "spotify_url": "https://open.spotify.com/search/Do%20It%20Again%20Elevation%20Worship","spotify_id": "3Xax7yHUjpC7RPJGU1Y5LD"},
    {"track_name": "Oceans",                "artist": "Hillsong United",     "album": "Zion",                         "image_url": None, "spotify_url": "https://open.spotify.com/search/Oceans%20Hillsong%20United",           "spotify_id": "3DarAbFujv6eYNliUTyqtz"},
    {"track_name": "Jireh",                 "artist": "Maverick City Music", "album": "Jubilee: Juneteenth Edition",  "image_url": None, "spotify_url": "https://open.spotify.com/search/Jireh%20Maverick%20City",             "spotify_id": "7oPgCQqMMXEXrNau5vxYZP"},
    {"track_name": "Fear Is Not My Future", "artist": "Kirk Franklin",       "album": "Father's Day",                 "image_url": None, "spotify_url": "https://open.spotify.com/search/Fear%20Is%20Not%20My%20Future%20Kirk%20Franklin","spotify_id": "2hGh5DVzdDMEkGiqnzYuNP"},
]


def _verify_match_access(db: Session, match_id: int, user_id: int):
    """Verify user belongs to this match. Returns the match or raises 403."""
    match = get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
    if user_id not in (match.user1_id, match.user2_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your match.")
    return match


@router.get("/{match_id}", response_model=list[MessageResponse])
def get_conversation(
    match_id: int,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get messages for a match conversation."""
    _verify_match_access(db, match_id, current_user.id)
    messages = get_messages(db, match_id, limit=limit, offset=offset)
    return messages


@router.post("/{match_id}", response_model=MessageResponse)
def send_message(
    match_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message in a match conversation."""
    _verify_match_access(db, match_id, current_user.id)

    if request.message_type not in ("text", "song_share"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="message_type must be 'text' or 'song_share'.",
        )

    if request.message_type == "song_share" and not request.song_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="song_data is required for song_share messages.",
        )

    song_dict = request.song_data.model_dump() if request.song_data else None

    msg = create_message(
        db,
        match_id=match_id,
        sender_id=current_user.id,
        content=request.content,
        message_type=request.message_type,
        song_data=song_dict,
    )
    return msg


@router.put("/{match_id}/read")
def read_messages(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all messages from the other user as read."""
    _verify_match_access(db, match_id, current_user.id)
    count = mark_messages_read(db, match_id, current_user.id)
    return {"marked_read": count}


@router.get("/unread/count", response_model=UnreadCountResponse)
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get unread message counts across all matches."""
    matches = get_matches(db, current_user.id)
    match_ids = [m.id for m in matches]
    by_match = get_unread_count(db, current_user.id, match_ids)
    total = sum(by_match.values())
    return UnreadCountResponse(total=total, by_match=by_match)


@router.get("/prompts/list")
def chat_prompts():
    """Get music-based conversation starters."""
    return {"prompts": CONVERSATION_PROMPTS}


@router.get("/search-song/results", response_model=list[SongSearchResult])
def search_song(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search for songs to share in chat. Uses real Spotify search when connected."""
    query = q.lower()

    if is_mock_mode():
        results = [
            s for s in MOCK_SONG_RESULTS
            if query in s["track_name"].lower() or query in s["artist"].lower()
        ]
        return results[:10]

    # Use real Spotify search API
    tokens = get_spotify_tokens(db, current_user.id)
    if not tokens:
        # Fall back to mock if user hasn't connected Spotify
        results = [
            s for s in MOCK_SONG_RESULTS
            if query in s["track_name"].lower() or query in s["artist"].lower()
        ]
        return results[:10]

    access_token = tokens.access_token
    if tokens.expires_at <= datetime.utcnow():
        try:
            refreshed = refresh_access_token(tokens.refresh_token)
            save_spotify_tokens(
                db, current_user.id,
                access_token=refreshed["access_token"],
                refresh_token=refreshed["refresh_token"],
                expires_at=refreshed["expires_at"],
            )
            access_token = refreshed["access_token"]
        except Exception:
            pass

    try:
        return search_tracks(access_token, q.strip())
    except Exception:
        results = [
            s for s in MOCK_SONG_RESULTS
            if query in s["track_name"].lower() or query in s["artist"].lower()
        ]
        return results[:10]
