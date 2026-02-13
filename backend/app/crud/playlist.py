from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.playlist import PlaylistMember, SharedPlaylist, WeeklyRecap


def create_playlist(
    db: Session,
    name: str,
    created_by: int,
    playlist_type: str = "match",
    description: str | None = None,
    match_id: int | None = None,
    tracks: list | None = None,
) -> SharedPlaylist:
    playlist = SharedPlaylist(
        name=name,
        description=description,
        created_by=created_by,
        playlist_type=playlist_type,
        match_id=match_id,
        tracks=tracks or [],
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


def get_playlist(db: Session, playlist_id: int) -> SharedPlaylist | None:
    return db.query(SharedPlaylist).filter(
        SharedPlaylist.id == playlist_id,
        SharedPlaylist.is_active == True,  # noqa: E712
    ).first()


def get_user_playlists(db: Session, user_id: int) -> list[SharedPlaylist]:
    playlist_ids = db.query(PlaylistMember.playlist_id).filter(
        PlaylistMember.user_id == user_id,
    ).subquery()
    return db.query(SharedPlaylist).filter(
        SharedPlaylist.id.in_(playlist_ids),
        SharedPlaylist.is_active == True,  # noqa: E712
    ).order_by(SharedPlaylist.updated_at.desc()).all()


def add_member(db: Session, playlist_id: int, user_id: int, role: str = "editor") -> PlaylistMember:
    member = PlaylistMember(playlist_id=playlist_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_member(db: Session, playlist_id: int, user_id: int) -> PlaylistMember | None:
    return db.query(PlaylistMember).filter(
        PlaylistMember.playlist_id == playlist_id,
        PlaylistMember.user_id == user_id,
    ).first()


def remove_member(db: Session, playlist_id: int, user_id: int) -> bool:
    member = get_member(db, playlist_id, user_id)
    if not member:
        return False
    db.delete(member)
    db.commit()
    return True


def get_members(db: Session, playlist_id: int) -> list[PlaylistMember]:
    return db.query(PlaylistMember).filter(
        PlaylistMember.playlist_id == playlist_id,
    ).all()


def add_track(db: Session, playlist_id: int, track: dict, added_by: int) -> SharedPlaylist:
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return None
    tracks = list(playlist.tracks or [])
    track["added_by"] = added_by
    track["added_at"] = datetime.utcnow().isoformat()
    tracks.append(track)
    playlist.tracks = tracks
    playlist.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(playlist)
    return playlist


def remove_track(db: Session, playlist_id: int, spotify_id: str) -> SharedPlaylist:
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return None
    tracks = [t for t in (playlist.tracks or []) if t.get("spotify_id") != spotify_id]
    playlist.tracks = tracks
    playlist.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(playlist)
    return playlist


def get_playlist_by_match(db: Session, match_id: int) -> SharedPlaylist | None:
    return db.query(SharedPlaylist).filter(
        SharedPlaylist.match_id == match_id,
        SharedPlaylist.is_active == True,  # noqa: E712
    ).first()


def generate_weekly_recap(db: Session, playlist_id: int) -> WeeklyRecap | None:
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return None

    now = datetime.utcnow()
    week_start = (now - timedelta(days=now.weekday())).date()

    # Count tracks added this week
    tracks = playlist.tracks or []
    week_tracks = []
    contributor_counts = {}
    for t in tracks:
        added_at = t.get("added_at")
        if added_at:
            try:
                added_date = datetime.fromisoformat(added_at).date()
                if added_date >= week_start:
                    week_tracks.append(t)
                    added_by = t.get("added_by", 0)
                    contributor_counts[added_by] = contributor_counts.get(added_by, 0) + 1
            except (ValueError, TypeError):
                pass

    top_contributor = max(contributor_counts, key=contributor_counts.get) if contributor_counts else None

    recap_data = {
        "tracks_added": len(week_tracks),
        "top_contributor": top_contributor,
        "total_tracks": len(tracks),
        "week_tracks": [{"track_name": t["track_name"], "artist": t["artist"]} for t in week_tracks],
    }

    recap = WeeklyRecap(
        playlist_id=playlist_id,
        week_start=week_start,
        recap_data=recap_data,
    )
    db.add(recap)
    db.commit()
    db.refresh(recap)
    return recap


def get_latest_recap(db: Session, playlist_id: int) -> WeeklyRecap | None:
    return db.query(WeeklyRecap).filter(
        WeeklyRecap.playlist_id == playlist_id,
    ).order_by(WeeklyRecap.created_at.desc()).first()
