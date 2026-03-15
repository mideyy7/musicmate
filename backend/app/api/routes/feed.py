from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.daily_tune import DailyTune, Reaction
from app.models.match import Match
from app.models.music_profile import MusicProfile
import json

router = APIRouter(prefix="/api/feed", tags=["feed"])

@router.get("")
def get_campus_pulse(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get Campus Pulse data: top songs, friend favorites, campus icons, genre pulse."""

    # Campus Top 50 - most liked songs from daily tunes
    # Aggregate song_name + artist combos by likes
    top_songs_raw = db.query(
        DailyTune.song_name,
        DailyTune.artist,
        func.count(Reaction.id).label("like_count")
    ).outerjoin(Reaction, (Reaction.daily_tune_id == DailyTune.id) & (Reaction.reaction_type == "like")
    ).group_by(DailyTune.song_name, DailyTune.artist
    ).order_by(desc("like_count")
    ).limit(50).all()

    campus_top_50 = [
        {"rank": i + 1, "song_name": row.song_name, "artist": row.artist, "likes": row.like_count}
        for i, row in enumerate(top_songs_raw)
    ]

    # Friend Favorites - what friends (matches) are currently "playing" (their last posted tune)
    # Get user's matches
    matches = db.query(Match).filter(
        (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)
    ).all()

    friend_ids = []
    for m in matches:
        fid = m.user2_id if m.user1_id == current_user.id else m.user1_id
        friend_ids.append(fid)

    friend_favorites = []
    for fid in friend_ids[:6]:
        friend = db.query(User).filter(User.id == fid).first()
        last_tune = db.query(DailyTune).filter(DailyTune.user_id == fid).order_by(desc(DailyTune.created_at)).first()
        if friend and last_tune:
            friend_favorites.append({
                "user_id": fid,
                "display_name": friend.display_name,
                "profile_picture": friend.profile_picture,
                "song_name": last_tune.song_name,
                "artist": last_tune.artist,
            })

    # Campus Icons - most listened-to artists (from music profiles)
    artist_counts = {}
    all_profiles = db.query(MusicProfile).all()
    for profile in all_profiles:
        try:
            top_artists = json.loads(profile.top_artists) if isinstance(profile.top_artists, str) else (profile.top_artists or [])
            for artist in top_artists[:5]:
                if isinstance(artist, dict):
                    name = artist.get("name", "")
                    img = artist.get("image_url", None)
                else:
                    name = str(artist)
                    img = None
                if name:
                    if name not in artist_counts:
                        artist_counts[name] = {"count": 0, "image_url": img}
                    artist_counts[name]["count"] += 1
        except Exception:
            continue

    campus_icons = sorted(
        [{"name": k, "image_url": v["image_url"], "count": v["count"]} for k, v in artist_counts.items()],
        key=lambda x: -x["count"]
    )[:8]

    # Genre Pulse - top genres across all profiles
    genre_counts = {}
    total_genre_entries = 0
    for profile in all_profiles:
        try:
            genres = json.loads(profile.top_genres) if isinstance(profile.top_genres, str) else (profile.top_genres or [])
            for genre in genres[:5]:
                if isinstance(genre, str):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
                    total_genre_entries += 1
        except Exception:
            continue

    genre_pulse = []
    if total_genre_entries > 0:
        genre_pulse = sorted(
            [{"genre": k, "percentage": round(v / total_genre_entries * 100)} for k, v in genre_counts.items()],
            key=lambda x: -x["percentage"]
        )[:6]

    return {
        "campus_top_50": campus_top_50,
        "friend_favorites": friend_favorites,
        "campus_icons": campus_icons,
        "genre_pulse": genre_pulse,
    }
