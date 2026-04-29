"""
Command line runner for the Music Recommender Simulation.

Run with:  python src/main.py
Requires:  ANTHROPIC_API_KEY environment variable to be set.
"""

from recommender import load_songs, recommend_songs
from ai_layer import parse_user_query, explain_recommendations


def main() -> None:
    songs = load_songs("data/songs.csv")

    print("\n=== AI Music Recommender ===")
    print("Describe the music you're in the mood for, or type 'quit' to exit.\n")

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not user_query:
            continue

        print("\nParsing your request...")
        try:
            user_prefs = parse_user_query(user_query)
        except Exception as e:
            print(f"Could not parse your request: {e}\n")
            continue

        print(f"Understood preferences: {user_prefs}")

        recommendations = recommend_songs(user_prefs, songs, k=5)

        print("\nTop 5 recommendations:\n")
        for song, score, _ in recommendations:
            print(f"  {song['title']} by {song['artist']} (score: {score:.2f})")

        print("\nGenerating explanations...")
        try:
            explanation = explain_recommendations(user_query, recommendations)
            print(f"\n{explanation}\n")
        except Exception as e:
            print(f"Could not generate explanation: {e}\n")


# --- Original hardcoded test cases (kept for reference) ---
# user_prefs = {"genre": "lofi"}
# user_prefs = {"genre": "bossa nova", "mood": "zen", "energy": 0.5, "acoustic": True}
# user_prefs = {"genre": "metal", "mood": "aggressive", "energy": 0.0, "acoustic": True}


if __name__ == "__main__":
    main()
