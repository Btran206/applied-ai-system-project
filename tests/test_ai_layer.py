"""
Evaluation tests for parse_user_query() in ai_layer.py.

Run:      pytest tests/test_recommender.py -v
Requires: ANTHROPIC_API_KEY environment variable to be set.
"""

import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ai_layer import parse_user_query

# ── Allowed values (must match the prompt in ai_layer.py) ────────────────────

VALID_GENRES = {
    "pop", "indie pop", "lofi", "ambient", "jazz", "folk", "country",
    "rock", "metal", "hip-hop", "r&b", "edm", "synthwave", "blues",
    "classical", "latin", "reggae",
}
VALID_MOODS = {
    "happy", "uplifting", "playful", "chill", "relaxed", "focused",
    "melancholic", "sad", "nostalgic", "intense", "aggressive", "energetic",
    "moody", "romantic", "confident", "soulful",
}

# ── Schema guardrail helper ───────────────────────────────────────────────────

def validate_schema(prefs: dict) -> list[str]:
    """Returns a list of schema errors. Used in every schema test."""
    errors = []
    for field in ("genre", "mood", "energy", "acoustic"):
        if field not in prefs:
            errors.append(f"missing required field '{field}'")
    if "genre" in prefs and prefs["genre"] not in VALID_GENRES:
        errors.append(f"genre '{prefs['genre']}' not in allowed list")
    if "mood" in prefs and prefs["mood"] not in VALID_MOODS:
        errors.append(f"mood '{prefs['mood']}' not in allowed list")
    if "energy" in prefs:
        if not isinstance(prefs["energy"], (int, float)):
            errors.append(f"energy must be a number, got {type(prefs['energy']).__name__}")
        elif not 0.0 <= float(prefs["energy"]) <= 1.0:
            errors.append(f"energy {prefs['energy']} outside [0.0, 1.0]")
    if "acoustic" in prefs and not isinstance(prefs["acoustic"], bool):
        errors.append(f"acoustic must be bool, got {type(prefs['acoustic']).__name__}")
    return errors

# ── Schema tests (hard — all inputs must return a valid, usable dict) ─────────

SCHEMA_INPUTS = [
    "something chill and acoustic for studying",
    "heavy metal music to get pumped at the gym",
    "upbeat pop songs for a house party",
    "smooth jazz for a late night drive",
    "sad acoustic folk music for a rainy afternoon",
    "asdfjklasdfjkl xyz",           # gibberish
    "music",                         # minimal input
    "calm but aggressive metal acoustic folk",  # contradictory
]

@pytest.mark.parametrize("query", SCHEMA_INPUTS)
def test_schema_is_valid(query):
    prefs = parse_user_query(query)
    errors = validate_schema(prefs)
    assert errors == [], f"Schema errors for input '{query}': {errors}"

# ── Semantic tests (soft — verify the model's interpretation is reasonable) ───

@pytest.mark.parametrize("query,field,expected", [
    ("something chill and acoustic for studying", "acoustic", True),
    ("something chill and acoustic for studying", "energy",   lambda v: v < 0.6),
    ("heavy metal music to get pumped at the gym", "acoustic", False),
    ("heavy metal music to get pumped at the gym", "energy",   lambda v: v > 0.6),
    ("upbeat pop songs for a house party",          "energy",   lambda v: v > 0.5),
    ("smooth jazz for a late night drive",          "genre",    "jazz"),
    ("sad acoustic folk music for a rainy afternoon", "acoustic", True),
    ("sad acoustic folk music for a rainy afternoon", "mood",
        lambda v: v in {"sad", "melancholic", "nostalgic"}),
])
def test_semantic_output(query, field, expected):
    prefs = parse_user_query(query)
    value = prefs.get(field)
    if callable(expected):
        assert expected(value), (
            f"Semantic check failed for '{query}': "
            f"field '{field}' = {value!r} did not satisfy expected condition"
        )
    else:
        assert value == expected, (
            f"Semantic check failed for '{query}': "
            f"field '{field}' expected {expected!r}, got {value!r}"
        )
