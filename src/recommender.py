from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Genres that are considered adjacent — earn 50% genre credit instead of 0
GENRE_CLUSTERS = {
    "pop":       {"indie pop", "synthwave"},
    "indie pop": {"pop"},
    "lofi":      {"ambient", "jazz", "classical"},
    "ambient":   {"lofi", "classical"},
    "jazz":      {"lofi", "r&b", "blues"},
    "folk":      {"country", "blues"},
    "country":   {"folk"},
    "rock":      {"metal"},
    "metal":     {"rock"},
    "hip-hop":   {"r&b"},
    "r&b":       {"hip-hop", "jazz"},
    "edm":       {"synthwave"},
    "synthwave":  {"edm", "pop"},
    "blues":     {"jazz", "folk"},
    "classical": {"ambient", "lofi"},
    "latin":     {"reggae"},
    "reggae":    {"latin"},
}

# Moods that are considered adjacent — earn 50% mood credit instead of 0
MOOD_CLUSTERS = {
    "happy":       {"uplifting", "playful"},
    "uplifting":   {"happy", "playful"},
    "playful":     {"happy", "uplifting"},
    "chill":       {"relaxed", "focused"},
    "relaxed":     {"chill", "focused"},
    "focused":     {"chill", "relaxed"},
    "melancholic": {"sad", "nostalgic", "soulful", "moody"},
    "sad":         {"melancholic", "nostalgic"},
    "nostalgic":   {"melancholic", "sad"},
    "intense":     {"aggressive", "energetic"},
    "aggressive":  {"intense", "energetic"},
    "energetic":   {"intense", "aggressive"},
    "moody":       {"melancholic", "romantic"},
    "romantic":    {"moody", "soulful"},
    "confident":   {"energetic"},
    "soulful":     {"melancholic", "romantic"},
}

# Moods where higher valence (more positive/cheerful) wins ties
HIGH_VALENCE_MOODS = {"happy", "uplifting", "playful", "energetic", "confident", "romantic"}
# Moods where lower valence (more somber/dark) wins ties
LOW_VALENCE_MOODS = {"sad", "melancholic", "nostalgic", "moody", "soulful", "aggressive", "intense"}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acoustic": user.likes_acoustic,
        }
        scored = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "acousticness": song.acousticness,
            }
            score, _ = score_song(user_prefs, song_dict)
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acoustic": user.likes_acoustic,
        }
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
        }
        _, reasons = score_song(user_prefs, song_dict)
        return ", ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Successfully loaded {len(songs)} songs.")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    if "genre" in user_prefs:
        if song["genre"] == user_prefs["genre"]:
            score += 0.35
            reasons.append("genre match (0.35)")
        elif song["genre"] in GENRE_CLUSTERS.get(user_prefs["genre"], set()):
            score += 0.175
            reasons.append("genre near-match (0.18)")
        else:
            reasons.append("genre mismatch (0.00)")
    else:
        reasons.append("genre (skipped)")

    if "mood" in user_prefs:
        if song["mood"] == user_prefs["mood"]:
            score += 0.25
            reasons.append("mood match (0.25)")
        elif song["mood"] in MOOD_CLUSTERS.get(user_prefs["mood"], set()):
            score += 0.125
            reasons.append("mood near-match (0.13)")
        else:
            reasons.append("mood mismatch (0.00)")
    else:
        reasons.append("mood (skipped)")

    if "energy" in user_prefs:
        energy_contrib = 0.25 * (1 - abs(song["energy"] - user_prefs["energy"]))
        score += energy_contrib
        reasons.append(f"energy fit ({energy_contrib:.2f})")
    else:
        reasons.append("energy (skipped)")

    if "acoustic" in user_prefs:
        acoustic_contrib = 0.15 * (1 - abs(song["acousticness"]))
        score += acoustic_contrib
        reasons.append(f"acoustic fit ({acoustic_contrib:.2f})")
    else:
        reasons.append("acoustic (skipped)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))

    mood = user_prefs.get("mood", "")
    if mood in HIGH_VALENCE_MOODS:
        valence_direction = 1    # ties broken by higher valence
    elif mood in LOW_VALENCE_MOODS:
        valence_direction = -1   # ties broken by lower valence
    else:
        valence_direction = 0    # no mood context — leave ties as stable sort

    scored.sort(key=lambda x: (x[1], valence_direction * x[0].get("valence", 0)), reverse=True)
    return scored[:k]
