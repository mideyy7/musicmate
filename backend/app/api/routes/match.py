from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.match import (
    check_mutual_like,
    create_match,
    create_swipe,
    get_candidates,
    get_match_by_id,
    get_matches,
    get_swipe,
)
from app.crud.playlist import add_member as add_playlist_member, create_playlist, get_playlist_by_match
from app.crud.spotify import get_music_profile
from app.models.user import User
from app.schemas.match import (
    CandidateResponse,
    CompatibilityBreakdown,
    MatchResponse,
    SwipeRequest,
    SwipeResponse,
)
from app.services.compatibility import compute_compatibility
from app.services.spotify import is_mock_mode

router = APIRouter(prefix="/api/match", tags=["match"])


@router.get("/feed", response_model=list[CandidateResponse])
def match_feed(
    course: str | None = Query(None),
    year: int | None = Query(None),
    faculty: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get swipe-ready candidates with compatibility scores."""
    my_profile = get_music_profile(db, current_user.id)
    if not my_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please sync your music profile first.",
        )

    candidates = get_candidates(db, current_user.id, course, year, faculty)

    results = []
    for user in candidates:
        their_profile = get_music_profile(db, user.id)
        if not their_profile:
            continue

        my_data = {
            "top_artists": my_profile.top_artists or [],
            "top_genres": my_profile.top_genres or [],
            "listening_patterns": my_profile.listening_patterns or {},
        }
        their_data = {
            "top_artists": their_profile.top_artists or [],
            "top_genres": their_profile.top_genres or [],
            "listening_patterns": their_profile.listening_patterns or {},
        }

        compat = compute_compatibility(my_data, their_data)

        top_artist_names = [a["name"] for a in (their_profile.top_artists or [])[:5]]

        results.append(CandidateResponse(
            user_id=user.id,
            display_name=user.display_name,
            course=user.course if user.show_course else None,
            year=user.year if user.show_year else None,
            faculty=user.faculty if user.show_faculty else None,
            compatibility_score=compat["score"],
            breakdown=CompatibilityBreakdown(
                shared_artists=compat["shared_artists"],
                shared_genres=compat["shared_genres"],
                genre_overlap_pct=compat["genre_overlap_pct"],
                artist_overlap_pct=compat["artist_overlap_pct"],
            ),
            top_artists=top_artist_names,
        ))

    results.sort(key=lambda c: c.compatibility_score, reverse=True)
    return results


@router.post("/swipe", response_model=SwipeResponse)
def swipe(
    request: SwipeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Like or pass on a user. Returns whether it's a mutual match."""
    if request.action not in ("like", "pass"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be 'like' or 'pass'.",
        )

    if request.target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot swipe on yourself.",
        )

    existing = get_swipe(db, current_user.id, request.target_user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already swiped on this user.",
        )

    create_swipe(db, current_user.id, request.target_user_id, request.action)

    # In mock mode, auto-generate a reciprocal like so testing works with a single user
    if request.action == "like" and is_mock_mode():
        reverse = get_swipe(db, request.target_user_id, current_user.id)
        if not reverse:
            create_swipe(db, request.target_user_id, current_user.id, "like")

    is_match = False
    match_id = None

    if request.action == "like" and check_mutual_like(db, current_user.id, request.target_user_id):
        my_profile = get_music_profile(db, current_user.id)
        their_profile = get_music_profile(db, request.target_user_id)

        score = 0
        breakdown = {}
        if my_profile and their_profile:
            my_data = {
                "top_artists": my_profile.top_artists or [],
                "top_genres": my_profile.top_genres or [],
                "listening_patterns": my_profile.listening_patterns or {},
            }
            their_data = {
                "top_artists": their_profile.top_artists or [],
                "top_genres": their_profile.top_genres or [],
                "listening_patterns": their_profile.listening_patterns or {},
            }
            compat = compute_compatibility(my_data, their_data)
            score = compat["score"]
            breakdown = compat

        match = create_match(db, current_user.id, request.target_user_id, score, breakdown)
        is_match = True
        match_id = match.id

        # Auto-create shared playlist for the match
        _auto_create_playlist(db, match, current_user, request.target_user_id, breakdown)

    return SwipeResponse(
        message="It's a match!" if is_match else "Swipe recorded.",
        is_match=is_match,
        match_id=match_id,
    )


@router.get("/matches", response_model=list[MatchResponse])
def list_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all matches for the current user."""
    matches = get_matches(db, current_user.id)

    results = []
    for match in matches:
        other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
        other_user = db.query(User).filter(User.id == other_id).first()
        if not other_user:
            continue

        breakdown = match.breakdown or {}
        results.append(MatchResponse(
            id=match.id,
            other_user={
                "id": other_user.id,
                "display_name": other_user.display_name,
                "course": other_user.course if other_user.show_course else None,
                "year": other_user.year if other_user.show_year else None,
                "faculty": other_user.faculty if other_user.show_faculty else None,
            },
            compatibility_score=match.compatibility_score,
            breakdown=CompatibilityBreakdown(
                shared_artists=breakdown.get("shared_artists", []),
                shared_genres=breakdown.get("shared_genres", []),
                genre_overlap_pct=breakdown.get("genre_overlap_pct", 0),
                artist_overlap_pct=breakdown.get("artist_overlap_pct", 0),
            ),
            created_at=match.created_at,
        ))

    return results


@router.get("/matches/{match_id}", response_model=MatchResponse)
def match_detail(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details for a specific match."""
    match = get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")

    if current_user.id not in (match.user1_id, match.user2_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your match.")

    other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
    other_user = db.query(User).filter(User.id == other_id).first()

    breakdown = match.breakdown or {}
    return MatchResponse(
        id=match.id,
        other_user={
            "id": other_user.id,
            "display_name": other_user.display_name,
            "course": other_user.course if other_user.show_course else None,
            "year": other_user.year if other_user.show_year else None,
            "faculty": other_user.faculty if other_user.show_faculty else None,
        },
        compatibility_score=match.compatibility_score,
        breakdown=CompatibilityBreakdown(
            shared_artists=breakdown.get("shared_artists", []),
            shared_genres=breakdown.get("shared_genres", []),
            genre_overlap_pct=breakdown.get("genre_overlap_pct", 0),
            artist_overlap_pct=breakdown.get("artist_overlap_pct", 0),
        ),
        created_at=match.created_at,
    )


def _auto_create_playlist(db: Session, match, current_user, target_user_id: int, breakdown: dict):
    """Create a shared playlist when a match is formed."""
    from datetime import datetime

    existing = get_playlist_by_match(db, match.id)
    if existing:
        return

    other_user = db.query(User).filter(User.id == target_user_id).first()
    if not other_user:
        return

    # Build initial tracks from shared artists
    my_profile = get_music_profile(db, current_user.id)
    their_profile = get_music_profile(db, target_user_id)

    initial_tracks = []
    if my_profile and their_profile:
        shared_artist_names = set(breakdown.get("shared_artists", []))
        all_tracks = (my_profile.recent_tracks or []) + (their_profile.recent_tracks or [])
        seen_ids = set()
        for t in all_tracks:
            if t.get("artist") in shared_artist_names and t.get("spotify_id") not in seen_ids:
                seen_ids.add(t["spotify_id"])
                initial_tracks.append({
                    "track_name": t.get("name", ""),
                    "artist": t.get("artist", ""),
                    "album": t.get("album", ""),
                    "image_url": t.get("image_url"),
                    "spotify_url": None,
                    "spotify_id": t["spotify_id"],
                    "added_by": current_user.id,
                    "added_at": datetime.utcnow().isoformat(),
                })

    playlist_name = f"{current_user.display_name} & {other_user.display_name}'s Mix"
    playlist = create_playlist(
        db,
        name=playlist_name,
        created_by=current_user.id,
        playlist_type="match",
        description=f"Shared playlist from your {match.compatibility_score:.0f}% music match!",
        match_id=match.id,
        tracks=initial_tracks,
    )

    add_playlist_member(db, playlist.id, current_user.id, role="owner")
    add_playlist_member(db, playlist.id, target_user_id, role="owner")
