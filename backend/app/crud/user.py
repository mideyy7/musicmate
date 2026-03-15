import secrets

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import hash_password


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    email: str,
    password: str,
    display_name: str,
    student_id: str | None = None,
    course: str | None = None,
    year: int | None = None,
    faculty: str | None = None,
    show_course: bool = True,
    show_year: bool = True,
    show_faculty: bool = True,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        display_name=display_name,
        student_id=student_id,
        course=course,
        year=year,
        faculty=faculty,
        show_course=show_course,
        show_year=show_year,
        show_faculty=show_faculty,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_cas_user(db: Session, email: str, display_name: str) -> User:
    """Create a user authenticated via UoM CAS. A random password is assigned
    since the user will always log in through CAS, not password."""
    random_password = secrets.token_hex(32)
    user = User(
        email=email,
        hashed_password=hash_password(random_password),
        display_name=display_name,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, updates: dict) -> User:
    for key, value in updates.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
