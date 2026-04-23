"""Load/save article lists with newest-first ordering."""

import json
from datetime import datetime
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


def dedupe_articles_by_url_newest_first(articles: list[dict]) -> list[dict]:
    """Keep newest occurrence per URL (input may be unsorted)."""
    ordered = sort_articles_by_timestamp_desc(articles)
    seen: set[str] = set()
    out: list[dict] = []
    for article in ordered:
        url = article.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(article)
    return out


def clip_articles_to_window(
    articles: list[dict], window_start: datetime, window_end: datetime
) -> list[dict]:
    """Keep articles with published_at in [window_start, window_end] (inclusive)."""
    clipped: list[dict] = []
    for article in articles:
        published = parse_iso_datetime(article.get("published_at", "") or "")
        if published is None:
            continue
        if window_start <= published <= window_end:
            clipped.append(article)
    return clipped


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
