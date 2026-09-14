"""Build the self-contained HTML presentation for the MDU PhD interview.

Reads _template.html, embeds the logo figures from ./Fig as base64 data URIs so the
deck is a single portable file, and writes
"PhD Interview - TA Dang Chuong.html".

Usage:  python build_presentation_html.py
"""

import base64
import mimetypes
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE / "Fig"
TEMPLATE = HERE / "_template.html"
OUTPUT = HERE / "PhD Interview - TA Dang Chuong.html"

FIGURES = {
    "__AVATAR__": "Picture1.png",
    "__DENSYS__": "DENSYS_Logo.png",
    "__REBASE__": "rebase.energy.png",
}


def as_data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def main() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")

    for token, filename in FIGURES.items():
        fig = FIG_DIR / filename
        if not fig.exists():
            raise FileNotFoundError(f"Missing figure: {fig}")
        html = html.replace(token, as_data_uri(fig))
        print(f"  embedded {filename:<22} ({fig.stat().st_size / 1024:6.1f} KB)")

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"\nWrote {OUTPUT.name}  ({OUTPUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
