from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.match import get_match_by_id, get_matches
from app.crud.message import create_message, get_messages, get_unread_count, mark_messages_read
from app.models.user import User
from app.schemas.message import (
    MessageResponse,
    SendMessageRequest,
    SongSearchResult,
    UnreadCountResponse,
)
from app.services.spotify import is_mock_mode

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
    {"track_name": "Blinding Lights", "artist": "The Weeknd", "album": "After Hours", "image_url": None, "spotify_url": None, "spotify_id": "0VjIjW4GlUZAMYd2vXMi4"},
    {"track_name": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "image_url": None, "spotify_url": None, "spotify_id": "4u7EnebtmKWzUH433cf5Qv"},
    {"track_name": "Levitating", "artist": "Dua Lipa", "album": "Future Nostalgia", "image_url": None, "spotify_url": None, "spotify_id": "39LLxExYz6ewLAo9BKIMH8"},
    {"track_name": "Heat Waves", "artist": "Glass Animals", "album": "Dreamland", "image_url": None, "spotify_url": None, "spotify_id": "02MWAaffLxlfxAUY7c5dvx"},
    {"track_name": "As It Was", "artist": "Harry Styles", "album": "Harry's House", "image_url": None, "spotify_url": None, "spotify_id": "4LRPiXqCikLlN15c3yImP7"},
    {"track_name": "Pink + White", "artist": "Frank Ocean", "album": "Blonde", "image_url": None, "spotify_url": None, "spotify_id": "3xKsf9qdS1CyvXSMEid6g8"},
    {"track_name": "505", "artist": "Arctic Monkeys", "album": "Favourite Worst Nightmare", "image_url": None, "spotify_url": None, "spotify_id": "0BxE4FqsDD1Ot4YuBXwAPp"},
    {"track_name": "Redbone", "artist": "Childish Gambino", "album": "Awaken, My Love!", "image_url": None, "spotify_url": None, "spotify_id": "0wXuerDYIBRqxJGzjEmjY4"},
    {"track_name": "Electric Feel", "artist": "MGMT", "album": "Oracular Spectacular", "image_url": None, "spotify_url": None, "spotify_id": "3FtYbEfBqAlGO46NUDQSAt"},
    {"track_name": "Ivy", "artist": "Frank Ocean", "album": "Blonde", "image_url": None, "spotify_url": None, "spotify_id": "2ZWlPOoWh0626oTaHrnl2a"},
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
):
    """Search for songs to share in chat."""
    query = q.lower()

    if is_mock_mode():
        results = [
            s for s in MOCK_SONG_RESULTS
            if query in s["track_name"].lower() or query in s["artist"].lower()
        ]
        return results[:10]

    # When real Spotify keys are provided, use the Spotify search API
    import httpx
    from app.core.config import settings

    # For now return mock results — real Spotify search would go here
    results = [
        s for s in MOCK_SONG_RESULTS
        if query in s["track_name"].lower() or query in s["artist"].lower()
    ]
    return results[:10]
