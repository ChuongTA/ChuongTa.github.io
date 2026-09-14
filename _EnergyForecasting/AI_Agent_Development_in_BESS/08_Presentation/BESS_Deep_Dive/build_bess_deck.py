"""Build the self-contained HTML deep-dive deck for the BESS AI-Agent GitHub project.

Reads _template.html, embeds the architecture diagram as a base64 data URI, and
writes "BESS AI-Agent - Implementation Deep Dive.html".

Usage:  python build_bess_deck.py
"""

import base64
import mimetypes
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "_template.html"
OUTPUT = HERE / "BESS AI-Agent - Implementation Deep Dive.html"

ARCH_IMG = HERE.parent.parent / "bess_agent_architecture.jpg"


def as_data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def main() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")

    if not ARCH_IMG.exists():
        raise FileNotFoundError(f"Missing architecture diagram: {ARCH_IMG}")
    html = html.replace("__ARCH__", as_data_uri(ARCH_IMG))
    print(f"  embedded {ARCH_IMG.name:<32} ({ARCH_IMG.stat().st_size / 1024:6.1f} KB)")

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"\nWrote {OUTPUT.name}  ({OUTPUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
