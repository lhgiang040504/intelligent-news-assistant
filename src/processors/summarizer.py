import re

from src.utils.text_utils import clean_text


def summarize_article(article: dict, max_sentences: int = 2) -> str:
    text = clean_text(article.get("content", "")) or clean_text(article.get("title", ""))
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chosen = [sentence for sentence in sentences if sentence][:max_sentences]
    if not chosen:
        return clean_text(article.get("title", ""))
    return " ".join(chosen)


def summarize_dataset(articles: list[dict], topic: str) -> str:
    if not articles:
        return f"No significant {topic.lower()} articles found in the selected window."

    sources = sorted({article.get("source", "Unknown") for article in articles})
    return (
        f"Collected {len(articles)} relevant {topic.lower()} articles from "
        f"{', '.join(sources)} during the last 7 days."
    )
