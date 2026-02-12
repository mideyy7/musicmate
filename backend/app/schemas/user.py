from datetime import datetime

from pydantic import BaseModel


class SSOInitRequest(BaseModel):
    email: str


class SSOCallbackData(BaseModel):
    email: str
    student_id: str | None = None
    course: str | None = None
    year: int | None = None
    faculty: str | None = None


class SSOCompleteRequest(BaseModel):
    email: str
    password: str
    display_name: str
    student_id: str | None = None
    course: str | None = None
    year: int | None = None
    faculty: str | None = None
    show_course: bool = True
    show_year: bool = True
    show_faculty: bool = True


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    course: str | None = None
    year: int | None = None
    faculty: str | None = None
    show_course: bool | None = None
    show_year: bool | None = None
    show_faculty: bool | None = None
    spotify_email: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    display_name: str
    student_id: str | None
    course: str | None
    year: int | None
    faculty: str | None
    show_course: bool
    show_year: bool
    show_faculty: bool
    spotify_email: str | None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
