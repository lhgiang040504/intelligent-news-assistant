"""Per-source JSON filenames under data/raw and data/processed."""

from pathlib import Path

# Stable slug -> filename like thanhnien_news.json
SOURCE_SLUG: dict[str, str] = {
    "VnExpress": "vnexpress",
    "Thanh Nien": "thanhnien",
    "Tuoi Tre": "tuoitre",
}


def source_slug(source_name: str) -> str:
    if source_name in SOURCE_SLUG:
        return SOURCE_SLUG[source_name]
    return "".join(c for c in source_name.lower() if c.isalnum()) or "unknown"


def raw_article_filename(source_name: str) -> str:
    return f"{source_slug(source_name)}_news.json"


def raw_article_path(raw_dir: str | Path, source_name: str) -> Path:
    return Path(raw_dir) / raw_article_filename(source_name)


def processed_article_path(processed_dir: str | Path, source_name: str) -> Path:
    return Path(processed_dir) / raw_article_filename(source_name)
