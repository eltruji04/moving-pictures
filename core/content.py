from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"


def read_markdown(relative_path):
    """Return the text of content/<relative_path>, or a placeholder if it doesn't exist yet."""
    path = CONTENT_DIR / relative_path
    if not path.exists():
        return "*Content coming soon.*"
    return path.read_text(encoding="utf-8")
