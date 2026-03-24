from datetime import datetime

from sqlalchemy.orm import Session

from app.models.spotify import SpotifyToken
from app.models.music_profile import MusicProfile


def get_spotify_tokens(db: Session, user_id: int) -> SpotifyToken | None:
    return db.query(SpotifyToken).filter(SpotifyToken.user_id == user_id).first()


def save_spotify_tokens(
    db: Session,
    user_id: int,
    access_token: str,
    refresh_token: str,
    expires_at: datetime,
    spotify_user_id: str | None = None,
) -> SpotifyToken:
    existing = get_spotify_tokens(db, user_id)
    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.expires_at = expires_at
        if spotify_user_id:
            existing.spotify_user_id = spotify_user_id
        db.commit()
        db.refresh(existing)
        return existing

    token = SpotifyToken(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        spotify_user_id=spotify_user_id,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def delete_spotify_tokens(db: Session, user_id: int) -> None:
    db.query(SpotifyToken).filter(SpotifyToken.user_id == user_id).delete()
    db.commit()


def get_music_profile(db: Session, user_id: int) -> MusicProfile | None:
    return db.query(MusicProfile).filter(MusicProfile.user_id == user_id).first()


def save_music_profile(db: Session, user_id: int, profile_data: dict) -> MusicProfile:
    existing = get_music_profile(db, user_id)
    if existing:
        existing.top_artists = profile_data["top_artists"]
        existing.top_genres = profile_data["top_genres"]
        existing.recent_tracks = profile_data["recent_tracks"]
        existing.listening_patterns = profile_data["listening_patterns"]
        existing.last_synced = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    profile = MusicProfile(
        user_id=user_id,
        top_artists=profile_data["top_artists"],
        top_genres=profile_data["top_genres"],
        recent_tracks=profile_data["recent_tracks"],
        listening_patterns=profile_data["listening_patterns"],
        last_synced=datetime.utcnow(),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def delete_music_profile(db: Session, user_id: int) -> None:
    db.query(MusicProfile).filter(MusicProfile.user_id == user_id).delete()
    db.commit()
