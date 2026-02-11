from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "musicmate-dev-secret-key-change-in-production"
    DATABASE_URL: str = "sqlite:///./db/app.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    ALLOWED_EMAIL_DOMAINS: list[str] = [
        "manchester.ac.uk",
        "student.manchester.ac.uk",
    ]

    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SPOTIFY_REDIRECT_URI: str = "http://localhost:5173/spotify/callback"

    class Config:
        env_file = ".env"


settings = Settings()
