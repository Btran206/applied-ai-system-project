import os
import json
from typing import Dict, List, Tuple
import anthropic

_client = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. "
                "Run: set ANTHROPIC_API_KEY=your-key-here"
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def parse_user_query(text: str) -> Dict:
    """
    Converts a plain-English music description into structured user preferences
    that can be passed directly to recommend_songs().
    """
    prompt = (
        f"You are a music preference parser. Extract structured preferences from this description:\n\n"
        f"\"{text}\"\n\n"
        "Return ONLY a JSON object with these fields:\n"
        "- \"genre\": one of: pop, indie pop, lofi, ambient, jazz, folk, country, rock, metal, hip-hop, r&b, edm, synthwave, blues, classical, latin, reggae\n"
        "- \"mood\": one of: happy, uplifting, playful, chill, relaxed, focused, melancholic, sad, nostalgic, intense, aggressive, energetic, moody, romantic, confident, soulful\n"
        "- \"energy\": a float between 0.0 (very calm) and 1.0 (very intense)\n"
        "- \"acoustic\": true if the user wants acoustic/unplugged sound, false for electronic/produced sound\n\n"
        "Pick the closest match for each field. Return only the JSON, no explanation."
    )

    message = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def explain_recommendations(user_query: str, recommendations: List[Tuple]) -> str:
    """
    Takes the user's original query and the top recommendations from recommend_songs(),
    and returns a human-friendly explanation of why each song was chosen.
    """
    songs_text = ""
    for i, (song, score, reasons) in enumerate(recommendations, 1):
        songs_text += (
            f"{i}. \"{song['title']}\" by {song['artist']}"
            f" (genre: {song['genre']}, mood: {song['mood']},"
            f" energy: {song['energy']}, score: {score:.2f})\n"
            f"   Score breakdown: {reasons}\n"
        )

    prompt = (
        f"A user asked for: \"{user_query}\"\n\n"
        f"The recommender system returned these songs:\n{songs_text}\n"
        "Adopt the persona of Snoop Dogg. Write a 1-2 sentence explanation for each song "
        "that feels like a vibe check. Use laid back, West Coast slang "
        "(e.g., 'nephew,' 'dig it,' 'smooth,' 'keep it G'). For every song, mention the "
        "genre, mood, or energy, but describe them like you're talking to a friend over a "
        "backyard BBQ. Keep it smooth, conversational, and rhythmic — make it sound like a legend."
    )

    message = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()
