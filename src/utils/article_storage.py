"""Load/save article lists with newest-first ordering."""

import json
from pathlib import Path

from src.utils.date_utils import parse_iso_datetime


def sort_articles_by_timestamp_desc(articles: list[dict]) -> list[dict]:
    """Sort by published_at descending (newest first). Missing dates sort last."""

    def sort_key(article: dict) -> tuple[int, str]:
        dt = parse_iso_datetime(article.get("published_at", "") or "")
        if dt is None:
            return (0, "")
        return (1, dt.isoformat())

    return sorted(articles, key=sort_key, reverse=True)


def save_articles_json(path: Path, articles: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sort_articles_by_timestamp_desc(articles)
    path.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_articles_json(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return data
