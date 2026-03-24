def compute_compatibility(profile1: dict, profile2: dict) -> dict:
    """Compute compatibility score between two music profiles.

    Weights:
    - Shared artists: 40%
    - Genre overlap (Jaccard): 40%
    - Listening pattern similarity: 20%

    Returns dict with score (0-100) and breakdown.
    """
    # Extract artist spotify_ids
    artists1 = {a["spotify_id"] for a in profile1.get("top_artists", [])}
    artists2 = {a["spotify_id"] for a in profile2.get("top_artists", [])}

    # Artist names for display
    artist_names1 = {a["spotify_id"]: a["name"] for a in profile1.get("top_artists", [])}
    artist_names2 = {a["spotify_id"]: a["name"] for a in profile2.get("top_artists", [])}

    shared_artist_ids = artists1 & artists2
    shared_artist_names = [
        artist_names1.get(aid) or artist_names2.get(aid)
        for aid in shared_artist_ids
    ]

    max_artists = max(len(artists1), len(artists2), 1)
    artist_overlap_pct = len(shared_artist_ids) / max_artists

    # Extract genres
    genres1 = {g["genre"] for g in profile1.get("top_genres", [])}
    genres2 = {g["genre"] for g in profile2.get("top_genres", [])}

    shared_genres = list(genres1 & genres2)
    genre_union = genres1 | genres2
    genre_overlap_pct = len(genres1 & genres2) / max(len(genre_union), 1)

    # Listening pattern similarity
    lp1 = profile1.get("listening_patterns", {})
    lp2 = profile2.get("listening_patterns", {})

    ta1 = lp1.get("total_artists", 0)
    ta2 = lp2.get("total_artists", 0)
    tg1 = lp1.get("total_genres", 0)
    tg2 = lp2.get("total_genres", 0)

    artist_count_sim = 1 - abs(ta1 - ta2) / max(ta1, ta2, 1)
    genre_count_sim = 1 - abs(tg1 - tg2) / max(tg1, tg2, 1)
    pattern_sim = (artist_count_sim + genre_count_sim) / 2

    # Weighted score
    score = (artist_overlap_pct * 40) + (genre_overlap_pct * 40) + (pattern_sim * 20)
    score = round(min(max(score, 0), 100))

    return {
        "score": score,
        "shared_artists": shared_artist_names,
        "shared_genres": shared_genres,
        "genre_overlap_pct": round(genre_overlap_pct, 3),
        "artist_overlap_pct": round(artist_overlap_pct, 3),
    }
