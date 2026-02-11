from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.user import create_user, get_user_by_email, update_user
from app.models.user import User
from app.schemas.user import (
    LoginRequest,
    ProfileUpdate,
    SSOCallbackData,
    SSOCompleteRequest,
    SSOInitRequest,
    Token,
    UserResponse,
)
from app.services.auth import (
    create_access_token,
    simulate_sso,
    validate_email_domain,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/sso/initiate", response_model=SSOCallbackData)
def sso_initiate(request: SSOInitRequest, db: Session = Depends(get_db)):
    """Start SSO flow. Validates email domain and returns simulated academic data."""
    if not validate_email_domain(request.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only University of Manchester email addresses are allowed. "
            "Please use your @manchester.ac.uk or @student.manchester.ac.uk email.",
        )

    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please log in instead.",
        )

    sso_data = simulate_sso(request.email)
    return SSOCallbackData(**sso_data)


@router.post("/sso/complete", response_model=Token)
def sso_complete(request: SSOCompleteRequest, db: Session = Depends(get_db)):
    """Complete SSO signup. Creates user account and returns JWT."""
    if not validate_email_domain(request.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only University of Manchester email addresses are allowed.",
        )

    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = create_user(
        db=db,
        email=request.email,
        password=request.password,
        display_name=request.display_name,
        student_id=request.student_id,
        course=request.course,
        year=request.year,
        faculty=request.faculty,
        show_course=request.show_course,
        show_year=request.show_year,
        show_faculty=request.show_faculty,
    )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password for returning users."""
    user = get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    updates: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile and visibility settings."""
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update.",
        )
    updated_user = update_user(db, current_user, update_data)
    return updated_user
