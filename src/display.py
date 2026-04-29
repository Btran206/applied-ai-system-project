import re
import textwrap

DIVIDER = "-" * 60
HEADER  = "=" * 60


def print_banner() -> None:
    print(f"\n{HEADER}")
    print("  AI Music Recommender")
    print(HEADER)
    print("  Describe the music you're in the mood for.")
    print("  Type 'quit' to exit.\n")


def print_prefs(prefs: dict) -> None:
    parts = [f"{k}: {v}" for k, v in prefs.items()]
    print(f"\n{DIVIDER}")
    print("  Understood Preferences")
    print(DIVIDER)
    print("  " + " | ".join(parts))


def print_picks(recommendations: list) -> None:
    print(f"\n{DIVIDER}")
    print("  TOP 5 PICKS")
    print(DIVIDER)
    for i, (song, score, _) in enumerate(recommendations, 1):
        left  = f"  {i}. {song['title']} - {song['artist']}"
        right = f"[score: {score:.2f}]"
        print(f"{left:<50} {right:>12}")


def print_explanation(text: str) -> None:
    header_re = re.compile(r"^\*{0,2}(\d+\.)\s+(.+?)\*{0,2}$")
    first = True

    print(f"\n{DIVIDER}")
    print("  Snoop's Take")
    print(DIVIDER)

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        m = header_re.match(stripped)
        if m:
            if not first:
                print(f"\n  {'-' * 56}")
            first = False
            num   = m.group(1)
            title = m.group(2).strip("*").strip()
            print(f"\n  {num} {title} -")
        else:
            clean = stripped.replace("**", "").replace("*", "")
            if clean:
                print(textwrap.fill(clean, width=56, initial_indent="    ", subsequent_indent="    "))
    print()
