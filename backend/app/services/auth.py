import random
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def validate_email_domain(email: str) -> bool:
    domain = email.split("@")[-1].lower()
    return domain in settings.ALLOWED_EMAIL_DOMAINS


def simulate_sso(email: str) -> dict:
    """Simulate a SAML SSO response from the University of Manchester.
    In production, this would be replaced with actual SAML IdP integration.
    """
    if not validate_email_domain(email):
        return None

    username = email.split("@")[0]
    faculties = [
        "Science and Engineering",
        "Humanities",
        "Biology, Medicine and Health",
    ]
    courses = [
        "Computer Science",
        "Mathematics",
        "Physics",
        "English Literature",
        "Psychology",
        "Medicine",
        "Law",
        "Economics",
        "Electrical Engineering",
        "Chemistry",
    ]

    return {
        "email": email,
        "student_id": f"{''.join(random.choices('0123456789', k=7))}",
        "course": random.choice(courses),
        "year": random.randint(1, 4),
        "faculty": random.choice(faculties),
    }
