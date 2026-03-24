"""
Demo seed: creates 14 gospel-music-loving UoM student accounts for pitch demos.
- 6 are pre-matched with the real user (mutual likes + chat messages)
- 8 appear in the swipe feed (have profiles, not yet matched)
Idempotent — safe to call on every login.
Swipe history for non-matched demo users is reset each login so
the feed always has fresh people to discover.
"""
import secrets
from sqlalchemy.orm import Session
from sqlalchemy import or_

from datetime import datetime

from app.models.user import User
from app.models.match import Match, Swipe
from app.models.daily_tune import DailyTune, Reaction
from app.crud.user import get_user_by_email
from app.crud.match import create_swipe, get_swipe, create_match
from app.crud.message import create_message
from app.crud.spotify import get_music_profile, save_music_profile, get_spotify_tokens, save_spotify_tokens
from app.crud.playlist import create_playlist, get_playlist_by_match
from app.crud.playlist import add_member as add_playlist_member
from app.services.auth import hash_password
from app.services.spotify import generate_mock_profile, search_tracks, refresh_access_token
from app.services.compatibility import compute_compatibility


def _get_valid_spotify_token(db: Session, user_id: int) -> str | None:
    """Get a valid Spotify access token for the user, refreshing if needed. Returns None in mock mode or if not connected."""
    from app.services.spotify import is_mock_mode
    if is_mock_mode():
        return None
    tokens = get_spotify_tokens(db, user_id)
    if not tokens or tokens.access_token == "mock_access_token":
        return None
    if tokens.expires_at <= datetime.utcnow():
        try:
            refreshed = refresh_access_token(tokens.refresh_token)
            save_spotify_tokens(db, user_id,
                access_token=refreshed["access_token"],
                refresh_token=refreshed["refresh_token"],
                expires_at=refreshed["expires_at"],
                spotify_user_id=tokens.spotify_user_id,
            )
            return refreshed["access_token"]
        except Exception:
            return None
    return tokens.access_token


def _fetch_track_metadata(db: Session, real_user_id: int, song_name: str, artist: str) -> dict:
    """Search Spotify for a track and return spotify_id, spotify_url, cover_image, preview_url."""
    token = _get_valid_spotify_token(db, real_user_id)
    if not token:
        return {}
    try:
        results = search_tracks(token, f"{song_name} {artist}", limit=1)
        if results:
            t = results[0]
            return {
                "spotify_id":  t.get("spotify_id"),
                "spotify_url": t.get("spotify_url"),
                "cover_image": t.get("image_url"),
                "preview_url": t.get("preview_url"),
            }
    except Exception:
        pass
    return {}


# Gospel songs for the campus feed — real Spotify track IDs
DEMO_TUNES = [
    {"song_name": "Way Maker",            "artist": "Sinach",              "spotify_id": "6y0igZArWVi6Iz0rj35c1Y", "spotify_url": "https://open.spotify.com/search/Way%20Maker%20Sinach"},
    {"song_name": "The Blessing",         "artist": "Elevation Worship",   "spotify_id": "3Blp2bAlBcxp8CBPF0T8W7", "spotify_url": "https://open.spotify.com/search/The%20Blessing%20Elevation%20Worship"},
    {"song_name": "Goodness of God",      "artist": "CeCe Winans",         "spotify_id": "1xR3kzx9OHTQP6UPKfSQfz", "spotify_url": "https://open.spotify.com/search/Goodness%20of%20God%20CeCe%20Winans"},
    {"song_name": "What A Beautiful Name","artist": "Hillsong Worship",    "spotify_id": "0BjC1NfoEOOusryehmNe5R", "spotify_url": "https://open.spotify.com/search/What%20A%20Beautiful%20Name%20Hillsong"},
    {"song_name": "Joyful",               "artist": "Dante Bowe",          "spotify_id": "0MoSqJpK8mglxq5W7YsJmj", "spotify_url": "https://open.spotify.com/search/Joyful%20Dante%20Bowe"},
    {"song_name": "Reckless Love",        "artist": "Cory Asbury",         "spotify_id": "1ZiP6JjWZCzFQvKNiOuvAi", "spotify_url": "https://open.spotify.com/search/Reckless%20Love%20Cory%20Asbury"},
    {"song_name": "Do It Again",          "artist": "Elevation Worship",   "spotify_id": "3Xax7yHUjpC7RPJGU1Y5LD", "spotify_url": "https://open.spotify.com/search/Do%20It%20Again%20Elevation%20Worship"},
    {"song_name": "Never Lost",           "artist": "Elevation Worship",   "spotify_id": "4M9HFQu9oAHRPKTtXFCjxP", "spotify_url": "https://open.spotify.com/search/Never%20Lost%20Elevation%20Worship"},
    {"song_name": "Talking to Jesus",     "artist": "Elevation Worship",   "spotify_id": "2nLtzopw4rPReszdYBJU6h", "spotify_url": "https://open.spotify.com/search/Talking%20to%20Jesus%20Elevation%20Worship"},
    {"song_name": "Holy Forever",         "artist": "Bethel Music",        "spotify_id": "3yGA4mQa7p9pCh4TRMflDr", "spotify_url": "https://open.spotify.com/search/Holy%20Forever%20Bethel%20Music"},
    {"song_name": "Oceans",               "artist": "Hillsong United",     "spotify_id": "3DarAbFujv6eYNliUTyqtz", "spotify_url": "https://open.spotify.com/search/Oceans%20Hillsong%20United"},
    {"song_name": "Made a Way",           "artist": "Travis Greene",       "spotify_id": "1HEvB0GRgBDMTU3oHbJXVA", "spotify_url": "https://open.spotify.com/search/Made%20a%20Way%20Travis%20Greene"},
    {"song_name": "You Know My Name",     "artist": "Tasha Cobbs Leonard", "spotify_id": "2hGh5DVzdDMEkGiqnzYuNP", "spotify_url": "https://open.spotify.com/search/You%20Know%20My%20Name%20Tasha%20Cobbs"},
    {"song_name": "Jireh",                "artist": "Maverick City Music", "spotify_id": "7oPgCQqMMXEXrNau5vxYZP", "spotify_url": "https://open.spotify.com/search/Jireh%20Maverick%20City%20Music"},
]

DEMO_STUDENTS = [
    # ── 6 pre-matched students ──────────────────────────────────────
    {
        "email": "adaeze.okafor.demo@student.manchester.ac.uk",
        "display_name": "Adaeze Okafor",
        "course": "Computer Science",
        "year": 2,
        "faculty": "Science and Engineering",
        "age": 20,
        "bio": "CS student and worship leader at UMSU Gospel Choir. Maverick City Music changed how I see worship. Always hunting for new gospel sounds!",
        "hobbies": "Worship leading, Coding, Photography",
        "profile_picture": "https://randomuser.me/api/portraits/women/1.jpg",
        "is_match": True,
        "seed_id": 10001,
        "messages": [
            "Omg we literally have the same gospel playlist 😭",
            "Have you heard Dante Bowe's latest? It's absolutely incredible",
        ],
    },
    {
        "email": "joshua.mensah.demo@student.manchester.ac.uk",
        "display_name": "Joshua Mensah",
        "course": "Music",
        "year": 2,
        "faculty": "Humanities",
        "age": 21,
        "bio": "Music student with a heart for gospel. I arrange worship music for our campus ministry and play keys every Sunday. Kirk Franklin is the GOAT.",
        "hobbies": "Piano, Choir directing, Basketball",
        "profile_picture": "https://randomuser.me/api/portraits/men/3.jpg",
        "is_match": True,
        "seed_id": 10002,
        "messages": [
            "Kirk Franklin literally has no bad songs, change my mind 🎹",
            "Your gospel music taste goes so hard ngl",
        ],
    },
    {
        "email": "grace.chen.demo@student.manchester.ac.uk",
        "display_name": "Grace Chen",
        "course": "Physics",
        "year": 2,
        "faculty": "Science and Engineering",
        "age": 20,
        "bio": "Physics student by day, Hillsong stan by night. Elevation Worship's 'Do It Again' literally carried me through first year exams.",
        "hobbies": "Guitar, Rock climbing, Bible study",
        "profile_picture": "https://randomuser.me/api/portraits/women/5.jpg",
        "is_match": True,
        "seed_id": 10003,
        "messages": [
            "The music compatibility is SO real 😍 we live on the same worship playlist",
            "Are you going to the gospel concert at the Academy this semester?",
        ],
    },
    {
        "email": "emmanuel.adeyemi.demo@student.manchester.ac.uk",
        "display_name": "Emmanuel Adeyemi",
        "course": "Music",
        "year": 1,
        "faculty": "Humanities",
        "age": 19,
        "bio": "First year Music student. Nigerian gospel runs in my blood — Dunsin Oyekan and Theophilus Sunday are everything. Learning to produce gospel beats.",
        "hobbies": "Music production, Football, Photography",
        "profile_picture": "https://randomuser.me/api/portraits/men/7.jpg",
        "is_match": True,
        "seed_id": 10004,
        "messages": [
            "Bro your gospel taste is absolutely ELITE 🔥",
            "We should collab on a worship set fr fr",
        ],
    },
    {
        "email": "blessing.nwachukwu.demo@student.manchester.ac.uk",
        "display_name": "Blessing Nwachukwu",
        "course": "Computer Science",
        "year": 3,
        "faculty": "Science and Engineering",
        "age": 21,
        "bio": "CS student who codes to Tasha Cobbs Leonard and CeCe Winans. Gospel music is my therapy and my motivation ✨",
        "hobbies": "Coding side projects, Dancing, Worship team",
        "profile_picture": "https://randomuser.me/api/portraits/women/9.jpg",
        "is_match": True,
        "seed_id": 10005,
        "messages": [
            "Tasha Cobbs' 'You Know My Name' is the most powerful song ever recorded, periodt ✨",
            "Your gospel picks on here are absolutely immaculate",
        ],
    },
    {
        "email": "caleb.osei.demo@student.manchester.ac.uk",
        "display_name": "Caleb Osei",
        "course": "Mechanical Engineering",
        "year": 2,
        "faculty": "Science and Engineering",
        "age": 21,
        "bio": "Engineer who unwinds with Elevation Worship and Travis Greene. Hillsong United are the most underrated worship band — always asking the deep questions.",
        "hobbies": "Cycling, Guitar, Campus ministry",
        "profile_picture": "https://randomuser.me/api/portraits/men/11.jpg",
        "is_match": True,
        "seed_id": 10006,
        "messages": [
            "Elevation Worship's live albums are unmatched and I will not hear otherwise",
            "Really glad we matched! Your gospel taste is absolutely fire 🎸",
        ],
    },
    # ── 8 swipe-feed students (not pre-matched, reset each login) ───
    {
        "email": "amara.diallo.demo@student.manchester.ac.uk",
        "display_name": "Amara Diallo",
        "course": "Biology",
        "year": 2,
        "faculty": "Biology, Medicine and Health",
        "age": 20,
        "bio": "Biology student surviving on Sinach and Lauren Daigle. 'Way Maker' got me through A-levels and it's still getting me through uni 💃",
        "hobbies": "Dancing, Cooking, Youth church",
        "profile_picture": "https://randomuser.me/api/portraits/women/13.jpg",
        "is_match": False,
        "seed_id": 10007,
        "messages": [],
    },
    {
        "email": "daniel.boateng.demo@student.manchester.ac.uk",
        "display_name": "Daniel Boateng",
        "course": "Philosophy",
        "year": 3,
        "faculty": "Humanities",
        "age": 22,
        "bio": "Philosophy major and gospel playlist curator. Jonathan McReynolds understands the deep questions better than most of my lecturers.",
        "hobbies": "Writing, Hiking, Gospel choir",
        "profile_picture": "https://randomuser.me/api/portraits/men/15.jpg",
        "is_match": False,
        "seed_id": 10008,
        "messages": [],
    },
    {
        "email": "zoe.williams.demo@student.manchester.ac.uk",
        "display_name": "Zoe Williams",
        "course": "Psychology",
        "year": 1,
        "faculty": "Humanities",
        "age": 19,
        "bio": "First year psych student. Obsessed with Maverick City Music and Phil Thompson. Worship music is genuinely the best therapy 😅",
        "hobbies": "Journaling, Running, Praise team",
        "profile_picture": "https://randomuser.me/api/portraits/women/17.jpg",
        "is_match": False,
        "seed_id": 10009,
        "messages": [],
    },
    {
        "email": "michael.asante.demo@student.manchester.ac.uk",
        "display_name": "Michael Asante",
        "course": "Medicine",
        "year": 4,
        "faculty": "Biology, Medicine and Health",
        "age": 23,
        "bio": "Med student kept alive by Chandler Moore and Maverick City. 'Joyful' is my revision playlist and I'm not apologising for it 🏥",
        "hobbies": "Gym, Chess, Campus worship",
        "profile_picture": "https://randomuser.me/api/portraits/men/19.jpg",
        "is_match": False,
        "seed_id": 10010,
        "messages": [],
    },
    {
        "email": "faith.ojo.demo@student.manchester.ac.uk",
        "display_name": "Faith Ojo",
        "course": "Law",
        "year": 2,
        "faculty": "Humanities",
        "age": 20,
        "bio": "Law student with a heart for African gospel. Dunsin Oyekan and Theophilus Sunday are permanently on repeat. Manchester gospel scene is so underrated!",
        "hobbies": "Spoken word, Netball, Church choir",
        "profile_picture": "https://randomuser.me/api/portraits/women/21.jpg",
        "is_match": False,
        "seed_id": 10011,
        "messages": [],
    },
    {
        "email": "samuel.kwame.demo@student.manchester.ac.uk",
        "display_name": "Samuel Kwame",
        "course": "Economics",
        "year": 3,
        "faculty": "Social Sciences",
        "age": 22,
        "bio": "Economics student by day, gospel music enthusiast always. Fred Hammond and Kirk Franklin taught me more about community than any textbook.",
        "hobbies": "Basketball, Chess, Worship production",
        "profile_picture": "https://randomuser.me/api/portraits/men/23.jpg",
        "is_match": False,
        "seed_id": 10012,
        "messages": [],
    },
    {
        "email": "naomi.phillips.demo@student.manchester.ac.uk",
        "display_name": "Naomi Phillips",
        "course": "Education",
        "year": 1,
        "faculty": "Humanities",
        "age": 19,
        "bio": "Future teacher who believes music education starts with gospel. CeCe Winans and Yolanda Adams — these voices shaped who I am!",
        "hobbies": "Teaching Sunday school, Running, Pottery",
        "profile_picture": "https://randomuser.me/api/portraits/women/25.jpg",
        "is_match": False,
        "seed_id": 10013,
        "messages": [],
    },
    {
        "email": "aaron.clarke.demo@student.manchester.ac.uk",
        "display_name": "Aaron Clarke",
        "course": "Civil Engineering",
        "year": 2,
        "faculty": "Science and Engineering",
        "age": 21,
        "bio": "Engineer building bridges by day, worshipping with Elevation Worship by night. 'Do It Again' has gotten me through every single deadline 🏗️",
        "hobbies": "Gym, Reading, Worship team sound",
        "profile_picture": "https://randomuser.me/api/portraits/men/27.jpg",
        "is_match": False,
        "seed_id": 10014,
        "messages": [],
    },
]


def _get_or_create_demo_user(db: Session, data: dict) -> User:
    existing = get_user_by_email(db, data["email"])
    if existing:
        # Keep profile picture up to date in case we changed it
        if existing.profile_picture != data["profile_picture"]:
            existing.profile_picture = data["profile_picture"]
            db.commit()
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
    Swipes for non-matched demo users are cleared each login so they
    always reappear in the match feed (at least 8 people to discover).
    """
    # Ensure the real user has a music profile (needed for compatibility scoring)
    real_profile = get_music_profile(db, real_user_id)
    if not real_profile:
        profile_data = generate_mock_profile(real_user_id)
        save_music_profile(db, real_user_id, profile_data)
        real_profile = get_music_profile(db, real_user_id)

    for i, data in enumerate(DEMO_STUDENTS):
        demo_user = _get_or_create_demo_user(db, data)

        # Ensure demo user has a music profile
        demo_profile = get_music_profile(db, demo_user.id)
        if not demo_profile:
            profile_data = generate_mock_profile(data["seed_id"])
            save_music_profile(db, demo_user.id, profile_data)
            demo_profile = get_music_profile(db, demo_user.id)

        # Seed a daily tune for this demo user (so they appear on Posts/Campus Pulse)
        _seed_daily_tune(db, demo_user.id, DEMO_TUNES[i % len(DEMO_TUNES)], real_user_id)

        if not data["is_match"]:
            # Reset the real user's swipe on this person each login
            # so they always reappear in the feed (fresh candidates every session)
            db.query(Swipe).filter(
                Swipe.user_id == real_user_id,
                Swipe.target_user_id == demo_user.id,
            ).delete(synchronize_session=False)
            db.commit()
            continue

        # Already matched? Skip match creation but still ensure messages exist
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


def _seed_daily_tune(db: Session, demo_user_id: int, tune: dict, real_user_id: int) -> None:
    """Post a daily tune for the demo user.
    On every login, backfills cover_image and preview_url using Spotify search
    so album art and playback work correctly for all demo posts.
    """
    # Fetch real metadata from Spotify (cover image + preview URL + correct ID)
    meta = _fetch_track_metadata(db, real_user_id, tune["song_name"], tune["artist"])

    existing = db.query(DailyTune).filter(DailyTune.user_id == demo_user_id).first()
    if existing:
        # Backfill missing fields on already-seeded tunes
        changed = False
        if meta.get("cover_image") and not existing.cover_image:
            existing.cover_image = meta["cover_image"]
            changed = True
        if meta.get("preview_url") and not existing.preview_url:
            existing.preview_url = meta["preview_url"]
            changed = True
        if meta.get("spotify_id") and not existing.spotify_id:
            existing.spotify_id = meta["spotify_id"]
            changed = True
        if changed:
            db.commit()
        return

    daily_tune = DailyTune(
        user_id=demo_user_id,
        song_name=tune["song_name"],
        artist=tune["artist"],
        spotify_id=meta.get("spotify_id") or tune["spotify_id"],
        spotify_url=meta.get("spotify_url") or tune["spotify_url"],
        cover_image=meta.get("cover_image"),
        preview_url=meta.get("preview_url"),
    )
    db.add(daily_tune)
    db.commit()
    db.refresh(daily_tune)
    # Add a like from the real user so it ranks in Campus Top 50
    like = Reaction(daily_tune_id=daily_tune.id, user_id=real_user_id, reaction_type="like")
    db.add(like)
    db.commit()


def _create_demo_playlist(db: Session, match: Match, real_user_id: int, demo_user: User) -> None:
    if get_playlist_by_match(db, match.id):
        return
    real_user = db.query(User).filter(User.id == real_user_id).first()
    if not real_user:
        return
    playlist = create_playlist(
        db,
        name=f"{real_user.display_name} & {demo_user.display_name}'s Worship Mix",
        created_by=real_user_id,
        playlist_type="match",
        description=f"Your shared gospel playlist — built on {match.compatibility_score:.0f}% music compatibility!",
        match_id=match.id,
        tracks=[],
    )
    add_playlist_member(db, playlist.id, real_user_id, role="owner")
    add_playlist_member(db, playlist.id, demo_user.id, role="owner")
