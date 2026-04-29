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
        print(f"{left:<46} {right:>13}")


def print_explanation(text: str) -> None:
    # A song header line starts with ** or * before the number (e.g. **1. or *1.)
    # or falls back to a bare number (1.) if the model omits markdown.
    header_re = re.compile(r"^\*+\d+\.|^\d+\.")

    blocks: list[tuple[str, list[str]]] = []
    current_header: str | None = None
    current_body: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if header_re.match(stripped):
            if current_header is not None:
                blocks.append((current_header, current_body))
            current_header = re.sub(r"\*+", "", stripped).strip()
            current_body = []
        elif current_header is not None:
            clean = re.sub(r"\*+", "", stripped).strip()
            if clean:
                current_body.append(clean)

    if current_header is not None:
        blocks.append((current_header, current_body))

    print(f"\n{DIVIDER}")
    print("  Snoop's Take")
    print(DIVIDER)

    for i, (header, body_lines) in enumerate(blocks):
        if i > 0:
            print(f"\n  {'-' * 56}")
        print(f"\n  {header} -")
        body_text = " ".join(body_lines)
        if body_text:
            print(textwrap.fill(body_text, width=56, initial_indent="    ", subsequent_indent="    "))
    print()
