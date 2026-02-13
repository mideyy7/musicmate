from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.match import get_match_by_id, get_matches
from app.crud.playlist import (
    add_member,
    add_track,
    create_playlist,
    generate_weekly_recap,
    get_latest_recap,
    get_member,
    get_members,
    get_playlist,
    get_playlist_by_match,
    get_user_playlists,
    remove_member,
    remove_track,
)
from app.crud.spotify import get_music_profile
from app.models.user import User
from app.schemas.playlist import (
    AddMemberRequest,
    AddTrackRequest,
    CreatePlaylistRequest,
    PlaylistMemberResponse,
    PlaylistResponse,
    PlaylistSummaryResponse,
    PlaylistTrack,
    WeeklyRecapResponse,
)
from app.services.compatibility import compute_compatibility

router = APIRouter(prefix="/api/playlist", tags=["playlist"])


def _build_playlist_response(db: Session, playlist) -> PlaylistResponse:
    members = get_members(db, playlist.id)
    member_responses = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            member_responses.append(PlaylistMemberResponse(
                user_id=user.id,
                display_name=user.display_name,
                role=m.role,
            ))

    tracks = [PlaylistTrack(**t) for t in (playlist.tracks or [])]

    return PlaylistResponse(
        id=playlist.id,
        name=playlist.name,
        description=playlist.description,
        playlist_type=playlist.playlist_type,
        match_id=playlist.match_id,
        spotify_playlist_id=playlist.spotify_playlist_id,
        track_count=len(tracks),
        member_count=len(member_responses),
        tracks=tracks,
        members=member_responses,
        created_at=playlist.created_at,
        updated_at=playlist.updated_at,
    )


@router.get("", response_model=list[PlaylistSummaryResponse])
def list_playlists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all playlists the user belongs to."""
    playlists = get_user_playlists(db, current_user.id)
    results = []
    for p in playlists:
        members = get_members(db, p.id)
        results.append(PlaylistSummaryResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            playlist_type=p.playlist_type,
            match_id=p.match_id,
            track_count=len(p.tracks or []),
            member_count=len(members),
            created_at=p.created_at,
        ))
    return results


@router.get("/{playlist_id}", response_model=PlaylistResponse)
def get_playlist_detail(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get playlist details including tracks and members."""
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found.")

    member = get_member(db, playlist_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this playlist.")

    return _build_playlist_response(db, playlist)


@router.post("", response_model=PlaylistResponse)
def create_new_playlist(
    request: CreatePlaylistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new group playlist."""
    playlist = create_playlist(
        db,
        name=request.name,
        created_by=current_user.id,
        playlist_type="group",
        description=request.description,
    )

    # Add creator as owner
    add_member(db, playlist.id, current_user.id, role="owner")

    # Add additional members
    if request.member_ids:
        for uid in request.member_ids:
            if uid != current_user.id:
                user = db.query(User).filter(User.id == uid).first()
                if user:
                    add_member(db, playlist.id, uid, role="editor")

    return _build_playlist_response(db, playlist)


@router.post("/{playlist_id}/tracks", response_model=PlaylistResponse)
def add_playlist_track(
    playlist_id: int,
    request: AddTrackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a track to the playlist."""
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found.")

    member = get_member(db, playlist_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this playlist.")

    # Check for duplicate
    existing_ids = {t.get("spotify_id") for t in (playlist.tracks or [])}
    if request.spotify_id in existing_ids:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Track already in playlist.")

    track_data = request.model_dump()
    updated = add_track(db, playlist_id, track_data, current_user.id)
    return _build_playlist_response(db, updated)


@router.delete("/{playlist_id}/tracks/{spotify_id}", response_model=PlaylistResponse)
def remove_playlist_track(
    playlist_id: int,
    spotify_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a track from the playlist."""
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found.")

    member = get_member(db, playlist_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this playlist.")

    updated = remove_track(db, playlist_id, spotify_id)
    return _build_playlist_response(db, updated)


@router.post("/{playlist_id}/members", response_model=PlaylistResponse)
def add_playlist_member(
    playlist_id: int,
    request: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a member to a group playlist (owner only)."""
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found.")

    if playlist.playlist_type != "group":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only add members to group playlists.")

    member = get_member(db, playlist_id, current_user.id)
    if not member or member.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can add members.")

    existing = get_member(db, playlist_id, request.user_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member.")

    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    add_member(db, playlist_id, request.user_id, role="editor")
    return _build_playlist_response(db, playlist)


@router.delete("/{playlist_id}/members/{user_id}", response_model=PlaylistResponse)
def remove_playlist_member(
    playlist_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a member from a group playlist (owner only)."""
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found.")

    if playlist.playlist_type != "group":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only remove members from group playlists.")

    member = get_member(db, playlist_id, current_user.id)
    if not member or member.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can remove members.")

    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself. Delete the playlist instead.")

    removed = remove_member(db, playlist_id, user_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    return _build_playlist_response(db, playlist)


@router.get("/{playlist_id}/recap", response_model=WeeklyRecapResponse | None)
def get_recap(
    playlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get or generate the weekly recap for a playlist."""
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found.")

    member = get_member(db, playlist_id, current_user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this playlist.")

    recap = get_latest_recap(db, playlist_id)
    if not recap:
        recap = generate_weekly_recap(db, playlist_id)

    if not recap:
        return None

    return WeeklyRecapResponse(
        id=recap.id,
        playlist_id=recap.playlist_id,
        week_start=recap.week_start,
        recap_data=recap.recap_data,
        created_at=recap.created_at,
    )


@router.post("/auto-create/{match_id}", response_model=PlaylistResponse)
def auto_create_match_playlist(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Auto-create a shared playlist for a match with shared tracks."""
    match = get_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")

    if current_user.id not in (match.user1_id, match.user2_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your match.")

    # Check if playlist already exists for this match
    existing = get_playlist_by_match(db, match_id)
    if existing:
        return _build_playlist_response(db, existing)

    other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
    other_user = db.query(User).filter(User.id == other_id).first()

    # Build shared tracks from both profiles
    my_profile = get_music_profile(db, current_user.id)
    their_profile = get_music_profile(db, other_id)

    initial_tracks = []
    if my_profile and their_profile:
        my_artists = {a["name"] for a in (my_profile.top_artists or [])}
        their_artists = {a["name"] for a in (their_profile.top_artists or [])}
        shared_artist_names = my_artists & their_artists

        # Add tracks from shared artists
        all_tracks = (my_profile.recent_tracks or []) + (their_profile.recent_tracks or [])
        seen_ids = set()
        for t in all_tracks:
            if t.get("artist") in shared_artist_names and t.get("spotify_id") not in seen_ids:
                seen_ids.add(t["spotify_id"])
                initial_tracks.append({
                    "track_name": t["name"],
                    "artist": t["artist"],
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
        match_id=match_id,
        tracks=initial_tracks,
    )

    add_member(db, playlist.id, current_user.id, role="owner")
    add_member(db, playlist.id, other_id, role="owner")

    return _build_playlist_response(db, playlist)
