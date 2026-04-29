"""
Command line runner for the Music Recommender Simulation.

Run with:  python src/main.py
Requires:  ANTHROPIC_API_KEY environment variable to be set.
"""

from recommender import load_songs, recommend_songs
from ai_layer import parse_user_query, explain_recommendations
from display import DIVIDER, print_banner, print_prefs, print_picks, print_explanation


def main() -> None:
    songs = load_songs("data/songs.csv")
    print_banner()

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ("quit", "exit", "q"):
            print("\nGoodbye!")
            break
        if not user_query:
            continue

        print("\n  Parsing your request...")
        try:
            user_prefs = parse_user_query(user_query)
        except Exception as e:
            print(f"\n  [Error] Could not parse request: {e}\n")
            continue

        print_prefs(user_prefs)

        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_picks(recommendations)

        print(f"\n  Generating explanations...")
        try:
            explanation = explain_recommendations(user_query, recommendations)
            print_explanation(explanation)
        except Exception as e:
            print(f"  [Error] Could not generate explanation: {e}")

        print(f"{DIVIDER}\n")


# --- Original hardcoded test cases (kept for reference) ---
# user_prefs = {"genre": "lofi"}
# user_prefs = {"genre": "bossa nova", "mood": "zen", "energy": 0.5, "acoustic": True}
# user_prefs = {"genre": "metal", "mood": "aggressive", "energy": 0.0, "acoustic": True}


if __name__ == "__main__":
    main()
