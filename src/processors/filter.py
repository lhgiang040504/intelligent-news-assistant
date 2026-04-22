from datetime import datetime

from src.utils.date_utils import parse_iso_datetime
from src.utils.text_utils import clean_text


def filter_articles(articles: list[dict], topic: str, start_time: datetime) -> list[dict]:
    topic_lower = topic.lower()
    filtered: list[dict] = []

    for article in articles:
        published = parse_iso_datetime(article.get("published_at", ""))
        if published is None or published < start_time:
            continue

        combined_text = clean_text(
            f"{article.get('title', '')} {article.get('content', '')}"
        ).lower()
        if topic_lower not in combined_text:
            continue

        filtered.append(article)

    return filtered
