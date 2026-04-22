from datetime import datetime

from src.utils.date_utils import parse_iso_datetime
from src.utils.text_utils import clean_text


def filter_articles(articles: list[dict], keywords: list[str], start_time: datetime) -> list[dict]:
    filtered: list[dict] = []
    keywords_lower = [keyword.lower() for keyword in keywords]

    for article in articles:
        published = parse_iso_datetime(article.get("published_at", ""))
        if published is None or published < start_time:
            continue

        combined_text = clean_text(
            f"{article.get('title', '')} {article.get('content', '')}"
        ).lower()
        
        if any(kw in combined_text for kw in keywords_lower):
            filtered.append(article)

    return filtered
