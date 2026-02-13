from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.message import Message


def create_message(
    db: Session,
    match_id: int,
    sender_id: int,
    content: str,
    message_type: str = "text",
    song_data: dict | None = None,
) -> Message:
    msg = Message(
        match_id=match_id,
        sender_id=sender_id,
        content=content,
        message_type=message_type,
        song_data=song_data,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(db: Session, match_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.match_id == match_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def mark_messages_read(db: Session, match_id: int, reader_id: int) -> int:
    count = (
        db.query(Message)
        .filter(
            Message.match_id == match_id,
            Message.sender_id != reader_id,
            Message.is_read == False,
        )
        .update({"is_read": True})
    )
    db.commit()
    return count


def get_unread_count(db: Session, user_id: int, match_ids: list[int]) -> dict[int, int]:
    if not match_ids:
        return {}

    rows = (
        db.query(Message.match_id, func.count(Message.id))
        .filter(
            Message.match_id.in_(match_ids),
            Message.sender_id != user_id,
            Message.is_read == False,
        )
        .group_by(Message.match_id)
        .all()
    )
    return {match_id: count for match_id, count in rows}
