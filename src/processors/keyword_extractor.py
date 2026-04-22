from collections import Counter

from src.utils.text_utils import tokenize


def extract_top_keywords(articles: list[dict], top_k: int = 10) -> list[tuple[str, int]]:
    token_counter: Counter[str] = Counter()
    for article in articles:
        text = f"{article.get('title', '')} {article.get('content', '')}"
        token_counter.update(tokenize(text))
    return token_counter.most_common(top_k)
