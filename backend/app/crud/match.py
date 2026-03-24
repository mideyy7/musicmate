from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.match import Match, Swipe
from app.models.music_profile import MusicProfile
from app.models.user import User


def create_swipe(db: Session, user_id: int, target_id: int, action: str) -> Swipe:
    swipe = Swipe(user_id=user_id, target_user_id=target_id, action=action)
    db.add(swipe)
    db.commit()
    db.refresh(swipe)
    return swipe


def get_swipe(db: Session, user_id: int, target_id: int) -> Swipe | None:
    return db.query(Swipe).filter(
        Swipe.user_id == user_id,
        Swipe.target_user_id == target_id,
    ).first()


def check_mutual_like(db: Session, user_id: int, target_id: int) -> bool:
    """Check if target has already liked user."""
    return db.query(Swipe).filter(
        Swipe.user_id == target_id,
        Swipe.target_user_id == user_id,
        Swipe.action == "like",
    ).first() is not None


def create_match(db: Session, user1_id: int, user2_id: int, score: float, breakdown: dict) -> Match:
    match = Match(
        user1_id=user1_id,
        user2_id=user2_id,
        compatibility_score=score,
        breakdown=breakdown,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def get_matches(db: Session, user_id: int) -> list[Match]:
    return db.query(Match).filter(
        or_(Match.user1_id == user_id, Match.user2_id == user_id)
    ).order_by(Match.created_at.desc()).all()


def get_match_by_id(db: Session, match_id: int) -> Match | None:
    return db.query(Match).filter(Match.id == match_id).first()


def get_swiped_user_ids(db: Session, user_id: int) -> set[int]:
    swipes = db.query(Swipe.target_user_id).filter(Swipe.user_id == user_id).all()
    return {s[0] for s in swipes}


def get_candidates(
    db: Session,
    user_id: int,
    course: str | None = None,
    year: int | None = None,
    faculty: str | None = None,
) -> list[User]:
    """Get users with music profiles, excluding self and already swiped."""
    swiped_ids = get_swiped_user_ids(db, user_id)
    exclude_ids = swiped_ids | {user_id}

    query = (
        db.query(User)
        .join(MusicProfile, MusicProfile.user_id == User.id)
        .filter(User.id.notin_(exclude_ids))
    )

    if course:
        query = query.filter(User.course == course)
    if year:
        query = query.filter(User.year == year)
    if faculty:
        query = query.filter(User.faculty == faculty)

    return query.all()
