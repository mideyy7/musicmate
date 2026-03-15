from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.daily_tune import DailyTune, Reaction
from pydantic import BaseModel

router = APIRouter(prefix="/api/posts", tags=["posts"])

class PostTuneRequest(BaseModel):
    song_name: str
    artist: str
    spotify_id: str | None = None
    spotify_url: str | None = None
    cover_image: str | None = None

class ReactRequest(BaseModel):
    reaction_type: str  # "like" or "dislike"

def get_post_response(tune: DailyTune, db: Session, current_user_id: int):
    user = db.query(User).filter(User.id == tune.user_id).first()
    likes = db.query(Reaction).filter(Reaction.daily_tune_id == tune.id, Reaction.reaction_type == "like").count()
    dislikes = db.query(Reaction).filter(Reaction.daily_tune_id == tune.id, Reaction.reaction_type == "dislike").count()
    my_reaction = db.query(Reaction).filter(Reaction.daily_tune_id == tune.id, Reaction.user_id == current_user_id).first()

    # Compute time ago
    diff = datetime.utcnow() - tune.created_at
    if diff.seconds < 3600:
        time_ago = f"{diff.seconds // 60} minutes ago"
    elif diff.days == 0:
        time_ago = f"{diff.seconds // 3600} hours ago"
    else:
        time_ago = f"{diff.days} days ago"

    return {
        "id": tune.id,
        "user_id": tune.user_id,
        "display_name": user.display_name if user else "Unknown",
        "profile_picture": user.profile_picture if user else None,
        "song_name": tune.song_name,
        "artist": tune.artist,
        "spotify_id": tune.spotify_id,
        "spotify_url": tune.spotify_url,
        "cover_image": tune.cover_image,
        "likes": likes,
        "dislikes": dislikes,
        "my_reaction": my_reaction.reaction_type if my_reaction else None,
        "created_at": tune.created_at.isoformat(),
        "time_ago": time_ago,
    }

@router.get("")
def get_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all daily tunes (most recent first)."""
    tunes = db.query(DailyTune).order_by(desc(DailyTune.created_at)).limit(50).all()
    return [get_post_response(t, db, current_user.id) for t in tunes]

@router.post("")
def post_tune(req: PostTuneRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Post a daily tune. One per user per day."""
    today = date.today().isoformat()
    # Check if user already posted today
    existing = db.query(DailyTune).filter(
        DailyTune.user_id == current_user.id,
        func.date(DailyTune.created_at) == today
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already posted your tune for today.")

    tune = DailyTune(
        user_id=current_user.id,
        song_name=req.song_name,
        artist=req.artist,
        spotify_id=req.spotify_id,
        spotify_url=req.spotify_url,
        cover_image=req.cover_image,
    )
    db.add(tune)

    # Update streak
    if current_user.last_tune_date == (date.today().replace(day=date.today().day - 1)).isoformat():
        current_user.daily_tune_streak = (current_user.daily_tune_streak or 0) + 1
    else:
        current_user.daily_tune_streak = 1
    current_user.last_tune_date = today

    db.commit()
    db.refresh(tune)
    return get_post_response(tune, db, current_user.id)

@router.post("/{tune_id}/react")
def react_to_tune(tune_id: int, req: ReactRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Like or dislike a daily tune."""
    tune = db.query(DailyTune).filter(DailyTune.id == tune_id).first()
    if not tune:
        raise HTTPException(status_code=404, detail="Tune not found.")

    existing = db.query(Reaction).filter(Reaction.daily_tune_id == tune_id, Reaction.user_id == current_user.id).first()
    if existing:
        if existing.reaction_type == req.reaction_type:
            # Toggle off
            db.delete(existing)
        else:
            existing.reaction_type = req.reaction_type
    else:
        reaction = Reaction(daily_tune_id=tune_id, user_id=current_user.id, reaction_type=req.reaction_type)
        db.add(reaction)

    db.commit()
    return get_post_response(tune, db, current_user.id)

@router.delete("/{tune_id}")
def delete_tune(tune_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tune = db.query(DailyTune).filter(DailyTune.id == tune_id, DailyTune.user_id == current_user.id).first()
    if not tune:
        raise HTTPException(status_code=404, detail="Tune not found.")
    db.delete(tune)
    db.commit()
    return {"ok": True}
