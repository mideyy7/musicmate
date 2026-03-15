from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil

from app.api.deps import get_current_user, get_db
from app.crud.user import create_cas_user, create_user, get_user_by_email, update_user
from app.models.user import User
from app.schemas.user import (
    CASCompleteRequest,
    CASInitiateResponse,
    CASTokenResponse,
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
from app.services.cas import generate_cas_url, verify_and_consume

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/cas/initiate", response_model=CASInitiateResponse)
def cas_initiate(callback_url: str = "http://localhost:5173/cas/callback"):
    """
    Start the UoM CAS login flow.
    Returns a CAS redirect URL and a one-time csticket.
    The frontend should store the csticket, then redirect the user to cas_url.
    CAS will redirect back to callback_url with ?username=&fullname= query params.
    """
    cas_url, csticket = generate_cas_url(callback_url)
    return CASInitiateResponse(cas_url=cas_url, csticket=csticket)


@router.post("/cas/complete", response_model=CASTokenResponse)
def cas_complete(request: CASCompleteRequest, db: Session = Depends(get_db)):
    """
    Complete the UoM CAS login flow.
    Verifies the csticket with the UoM CAS server, then creates or logs in the user.
    Returns a JWT and whether this is a new account (needs onboarding).
    """
    verified = verify_and_consume(request.csticket, request.username, request.fullname)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CAS verification failed. Please try signing in again.",
        )

    # Try student domain first, then fall back to staff domain for existing accounts
    email = f"{request.username}@student.manchester.ac.uk"
    existing_user = get_user_by_email(db, email)

    # Also check the old staff/legacy domain in case they have an existing account
    if not existing_user:
        legacy_email = f"{request.username}@manchester.ac.uk"
        existing_user = get_user_by_email(db, legacy_email)
        if existing_user:
            email = legacy_email

    if existing_user:
        access_token = create_access_token(data={"sub": str(existing_user.id)})
        return CASTokenResponse(access_token=access_token, is_new_user=False)

    user = create_cas_user(db, email=email, display_name=request.fullname)
    access_token = create_access_token(data={"sub": str(user.id)})
    return CASTokenResponse(access_token=access_token, is_new_user=True)


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


@router.post("/me/picture", response_model=UserResponse)
async def upload_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a profile picture."""
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"user_{current_user.id}{ext}"
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    url = f"/uploads/{filename}"
    updated = update_user(db, current_user, {"profile_picture": url})
    return updated
