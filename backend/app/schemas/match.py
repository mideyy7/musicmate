from datetime import datetime

from pydantic import BaseModel


class SwipeRequest(BaseModel):
    target_user_id: int
    action: str  # "like" or "pass"


class SwipeResponse(BaseModel):
    message: str
    is_match: bool
    match_id: int | None = None


class CompatibilityBreakdown(BaseModel):
    shared_artists: list[str]
    shared_genres: list[str]
    genre_overlap_pct: float
    artist_overlap_pct: float


class MatchResponse(BaseModel):
    id: int
    other_user: dict
    compatibility_score: float
    breakdown: CompatibilityBreakdown
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateResponse(BaseModel):
    user_id: int
    display_name: str
    course: str | None = None
    year: int | None = None
    faculty: str | None = None
    compatibility_score: float
    breakdown: CompatibilityBreakdown
    top_artists: list[str]
