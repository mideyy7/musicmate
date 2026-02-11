from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.spotify import (
    delete_music_profile,
    delete_spotify_tokens,
    get_music_profile,
    get_spotify_tokens,
    save_music_profile,
    save_spotify_tokens,
)
from app.models.user import User
from app.schemas.spotify import (
    MusicProfileResponse,
    SpotifyAuthURL,
    SpotifyCallbackRequest,
    SpotifyStatusResponse,
)
from app.services.spotify import (
    build_music_profile,
    exchange_code,
    fetch_recent_tracks,
    fetch_top_artists,
    fetch_top_tracks,
    get_auth_url,
    get_spotify_user_id,
    refresh_access_token,
)

router = APIRouter(prefix="/api/spotify", tags=["spotify"])


def _get_valid_token(db: Session, user_id: int) -> str:
    """Get a valid Spotify access token, refreshing if expired."""
    tokens = get_spotify_tokens(db, user_id)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spotify not connected. Please connect your Spotify account first.",
        )

    if tokens.expires_at <= datetime.utcnow():
        try:
            new_tokens = refresh_access_token(tokens.refresh_token)
            save_spotify_tokens(
                db,
                user_id,
                access_token=new_tokens["access_token"],
                refresh_token=new_tokens["refresh_token"],
                expires_at=new_tokens["expires_at"],
            )
            return new_tokens["access_token"]
        except Exception:
            delete_spotify_tokens(db, user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Spotify session expired. Please reconnect your Spotify account.",
            )

    return tokens.access_token


@router.get("/auth-url", response_model=SpotifyAuthURL)
def spotify_auth_url(current_user: User = Depends(get_current_user)):
    """Get Spotify authorization URL to start OAuth flow."""
    url = get_auth_url(state=str(current_user.id))
    return SpotifyAuthURL(auth_url=url)


@router.post("/callback", response_model=SpotifyStatusResponse)
def spotify_callback(
    request: SpotifyCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Exchange Spotify auth code for tokens and store them."""
    try:
        tokens = exchange_code(request.code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange Spotify code: {str(e)}",
        )

    spotify_user_id = get_spotify_user_id(tokens["access_token"])

    save_spotify_tokens(
        db,
        user_id=current_user.id,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_at=tokens["expires_at"],
        spotify_user_id=spotify_user_id,
    )

    return SpotifyStatusResponse(connected=True, spotify_user_id=spotify_user_id)


@router.get("/status", response_model=SpotifyStatusResponse)
def spotify_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if Spotify is connected for the current user."""
    tokens = get_spotify_tokens(db, current_user.id)
    if tokens:
        return SpotifyStatusResponse(connected=True, spotify_user_id=tokens.spotify_user_id)
    return SpotifyStatusResponse(connected=False)


@router.post("/sync", response_model=MusicProfileResponse)
def spotify_sync(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch latest Spotify data and build/update music profile."""
    access_token = _get_valid_token(db, current_user.id)

    try:
        top_artists = fetch_top_artists(access_token)
        top_tracks = fetch_top_tracks(access_token)
        recent_tracks = fetch_recent_tracks(access_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch Spotify data: {str(e)}",
        )

    profile_data = build_music_profile(top_artists, top_tracks, recent_tracks)
    profile = save_music_profile(db, current_user.id, profile_data)

    return MusicProfileResponse(
        top_artists=profile.top_artists,
        top_genres=profile.top_genres,
        recent_tracks=profile.recent_tracks,
        listening_patterns=profile.listening_patterns,
        last_synced=profile.last_synced,
    )


@router.get("/profile", response_model=MusicProfileResponse)
def spotify_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get stored music profile for the current user."""
    profile = get_music_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No music profile found. Please sync your Spotify data first.",
        )

    return MusicProfileResponse(
        top_artists=profile.top_artists,
        top_genres=profile.top_genres,
        recent_tracks=profile.recent_tracks,
        listening_patterns=profile.listening_patterns,
        last_synced=profile.last_synced,
    )


@router.delete("/disconnect")
def spotify_disconnect(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disconnect Spotify and remove stored data."""
    delete_spotify_tokens(db, current_user.id)
    delete_music_profile(db, current_user.id)
    return {"message": "Spotify disconnected successfully"}
