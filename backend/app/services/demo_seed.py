"""
Demo seed: creates 10 realistic UoM student accounts for pitch demos.
- 6 are pre-matched with the real user (mutual likes + chat messages)
- 4 appear in the swipe feed (have profiles, not yet matched)
Idempotent — safe to call on every login.
"""
import secrets
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.models.match import Match
from app.crud.user import get_user_by_email
from app.crud.match import create_swipe, get_swipe, create_match
from app.crud.message import create_message
from app.crud.spotify import get_music_profile, save_music_profile
from app.crud.playlist import create_playlist, get_playlist_by_match
from app.crud.playlist import add_member as add_playlist_member
from app.services.auth import hash_password
from app.services.spotify import generate_mock_profile
from app.services.compatibility import compute_compatibility


DEMO_STUDENTS = [
    # ── 6 pre-matched students ──────────────────────────────────────
    {
        "email": "emma.thompson.demo@student.manchester.ac.uk",
        "display_name": "Emma Thompson",
        "course": "Computer Science",
        "year": 2,
        "faculty": "Science and Engineering",
        "age": 20,
        "bio": "Coffee addict, indie music lover, and part-time code monkey. Always down to discover new artists!",
        "hobbies": "Hiking, Photography, Live music",
        "profile_picture": "https://i.pravatar.cc/300?img=5",
        "is_match": True,
        "seed_id": 10001,
        "messages": [
            "Hey! Just saw we have like 70% music compatibility 🎵 love your taste!",
            "Have you been to any gigs in Manchester recently?",
        ],
    },
    {
        "email": "james.okonkwo.demo@student.manchester.ac.uk",
        "display_name": "James Okonkwo",
        "course": "Mathematics",
        "year": 3,
        "faculty": "Science and Engineering",
        "age": 22,
        "bio": "Maths geek by day, jazz and hip-hop head by night. Frank Ocean is everything.",
        "hobbies": "Jazz piano, Football, Cooking",
        "profile_picture": "https://i.pravatar.cc/300?img=33",
        "is_match": True,
        "seed_id": 10002,
        "messages": [
            "Blonde is the greatest album of our generation and I will not take any criticism 😤",
            "Your music taste actually goes hard though ngl",
        ],
    },
    {
        "email": "sophie.chen.demo@student.manchester.ac.uk",
        "display_name": "Sophie Chen",
        "course": "Physics",
        "year": 2,
        "faculty": "Science and Engineering",
        "age": 20,
        "bio": "Physics student but my heart belongs to Tame Impala. Catch me at every indie concert in Manchester.",
        "hobbies": "Guitar, Rock climbing, Reading sci-fi",
        "profile_picture": "https://i.pravatar.cc/300?img=9",
        "is_match": True,
        "seed_id": 10003,
        "messages": [
            "Ok the music compatibility score is SO real 😍 we literally have the same taste",
            "Are you going to any concerts this semester?",
        ],
    },
    {
        "email": "marcus.williams.demo@student.manchester.ac.uk",
        "display_name": "Marcus Williams",
        "course": "Music",
        "year": 1,
        "faculty": "Humanities",
        "age": 19,
        "bio": "First year Music student. Into everything from hip-hop to ambient. Tyler, the Creator changed my life.",
        "hobbies": "Producing beats, Basketball, Photography",
        "profile_picture": "https://i.pravatar.cc/300?img=25",
        "is_match": True,
        "seed_id": 10004,
        "messages": [
            "Bro your music taste is actually elite 🔥",
            "We should make a collab playlist on here ngl",
        ],
    },
    {
        "email": "aisha.patel.demo@student.manchester.ac.uk",
        "display_name": "Aisha Patel",
        "course": "Computer Science",
        "year": 3,
        "faculty": "Science and Engineering",
        "age": 21,
        "bio": "CS student who codes to SZA and Billie Eilish. Big fan of R&B and alternative pop.",
        "hobbies": "Coding side projects, Dancing, Yoga",
        "profile_picture": "https://i.pravatar.cc/300?img=47",
        "is_match": True,
        "seed_id": 10005,
        "messages": [
            "SZA's SOS album is honestly one of the best things ever recorded ✨",
            "Your picks on here are immaculate by the way",
        ],
    },
    {
        "email": "liam.bradshaw.demo@student.manchester.ac.uk",
        "display_name": "Liam Bradshaw",
        "course": "Mechanical Engineering",
        "year": 2,
        "faculty": "Science and Engineering",
        "age": 21,
        "bio": "Engineer with a soft spot for indie folk and psychedelic rock. Lifelong Radiohead fan.",
        "hobbies": "Cycling, Guitar, Board games",
        "profile_picture": "https://i.pravatar.cc/300?img=11",
        "is_match": True,
        "seed_id": 10006,
        "messages": [
            "Kid A is legitimately one of the greatest albums ever recorded, no debate",
            "Really glad we matched! Your music taste is top tier 🎸",
        ],
    },
    # ── 4 swipe-feed students (not pre-matched) ─────────────────────
    {
        "email": "priya.sharma.demo@student.manchester.ac.uk",
        "display_name": "Priya Sharma",
        "course": "Biology",
        "year": 2,
        "faculty": "Biology, Medicine and Health",
        "age": 20,
        "bio": "Biology student surviving on Bad Bunny and Dua Lipa. Always up for a good time 💃",
        "hobbies": "Dancing, Cooking, Netflix",
        "profile_picture": "https://i.pravatar.cc/300?img=48",
        "is_match": False,
        "seed_id": 10007,
        "messages": [],
    },
    {
        "email": "daniel.foster.demo@student.manchester.ac.uk",
        "display_name": "Daniel Foster",
        "course": "Philosophy",
        "year": 3,
        "faculty": "Humanities",
        "age": 22,
        "bio": "Philosophy major and existentialist playlist curator. Lana Del Rey understands me better than most people.",
        "hobbies": "Writing, Hiking, Film photography",
        "profile_picture": "https://i.pravatar.cc/300?img=52",
        "is_match": False,
        "seed_id": 10008,
        "messages": [],
    },
    {
        "email": "chloe.martinez.demo@student.manchester.ac.uk",
        "display_name": "Chloe Martinez",
        "course": "Psychology",
        "year": 1,
        "faculty": "Humanities",
        "age": 19,
        "bio": "First year psych student. Obsessed with Phoebe Bridgers and sad indie. I promise I'm fine 😅",
        "hobbies": "Journaling, Running, Pottery",
        "profile_picture": "https://i.pravatar.cc/300?img=44",
        "is_match": False,
        "seed_id": 10009,
        "messages": [],
    },
    {
        "email": "noah.thompson.demo@student.manchester.ac.uk",
        "display_name": "Noah Thompson",
        "course": "Medicine",
        "year": 4,
        "faculty": "Biology, Medicine and Health",
        "age": 23,
        "bio": "Med student kept alive by Kendrick Lamar and caffeine. Nearly at the finish line 🏥",
        "hobbies": "Gym, Chess, Podcasts",
        "profile_picture": "https://i.pravatar.cc/300?img=67",
        "is_match": False,
        "seed_id": 10010,
        "messages": [],
    },
]


def _get_or_create_demo_user(db: Session, data: dict) -> User:
    existing = get_user_by_email(db, data["email"])
    if existing:
        return existing
    user = User(
        email=data["email"],
        hashed_password=hash_password(secrets.token_hex(32)),
        display_name=data["display_name"],
        course=data["course"],
        year=data["year"],
        faculty=data["faculty"],
        age=data["age"],
        bio=data["bio"],
        hobbies=data["hobbies"],
        profile_picture=data["profile_picture"],
        show_course=True,
        show_year=True,
        show_faculty=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed_demo_users(db: Session, real_user_id: int) -> None:
    """
    Create demo students and wire up pre-matches for the pitch demo.
    Idempotent — safe to call on every login.
    """
    # Ensure the real user has a music profile (needed for compatibility scoring)
    real_profile = get_music_profile(db, real_user_id)
    if not real_profile:
        profile_data = generate_mock_profile(real_user_id)
        save_music_profile(db, real_user_id, profile_data)
        real_profile = get_music_profile(db, real_user_id)

    for data in DEMO_STUDENTS:
        demo_user = _get_or_create_demo_user(db, data)

        # Ensure demo user has a music profile
        demo_profile = get_music_profile(db, demo_user.id)
        if not demo_profile:
            profile_data = generate_mock_profile(data["seed_id"])
            save_music_profile(db, demo_user.id, profile_data)
            demo_profile = get_music_profile(db, demo_user.id)

        if not data["is_match"]:
            continue

        # Already matched? Skip
        already_matched = db.query(Match).filter(
            or_(
                (Match.user1_id == real_user_id) & (Match.user2_id == demo_user.id),
                (Match.user1_id == demo_user.id) & (Match.user2_id == real_user_id),
            )
        ).first()
        if already_matched:
            continue

        # Create mutual swipes
        if not get_swipe(db, real_user_id, demo_user.id):
            create_swipe(db, real_user_id, demo_user.id, "like")
        if not get_swipe(db, demo_user.id, real_user_id):
            create_swipe(db, demo_user.id, real_user_id, "like")

        # Compute compatibility score
        score = 65.0
        breakdown: dict = {
            "shared_artists": [],
            "shared_genres": [],
            "genre_overlap_pct": 0.0,
            "artist_overlap_pct": 0.0,
        }
        if real_profile and demo_profile:
            compat = compute_compatibility(
                {
                    "top_artists": real_profile.top_artists or [],
                    "top_genres": real_profile.top_genres or [],
                    "listening_patterns": real_profile.listening_patterns or {},
                },
                {
                    "top_artists": demo_profile.top_artists or [],
                    "top_genres": demo_profile.top_genres or [],
                    "listening_patterns": demo_profile.listening_patterns or {},
                },
            )
            score = max(compat["score"], 55.0)  # floor at 55% for demo appeal
            breakdown = compat

        match = create_match(db, real_user_id, demo_user.id, score, breakdown)

        # Shared playlist
        _create_demo_playlist(db, match, real_user_id, demo_user)

        # Seed opening messages from the demo user
        for text in data["messages"]:
            create_message(db, match.id, demo_user.id, text)


def _create_demo_playlist(db: Session, match: Match, real_user_id: int, demo_user: User) -> None:
    if get_playlist_by_match(db, match.id):
        return
    real_user = db.query(User).filter(User.id == real_user_id).first()
    if not real_user:
        return
    playlist = create_playlist(
        db,
        name=f"{real_user.display_name} & {demo_user.display_name}'s Mix",
        created_by=real_user_id,
        playlist_type="match",
        description=f"Your shared playlist — built on {match.compatibility_score:.0f}% music compatibility!",
        match_id=match.id,
        tracks=[],
    )
    add_playlist_member(db, playlist.id, real_user_id, role="owner")
    add_playlist_member(db, playlist.id, demo_user.id, role="owner")
