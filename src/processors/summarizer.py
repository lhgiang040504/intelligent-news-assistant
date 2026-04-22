# import re

# from src.utils.text_utils import clean_text


# def summarize_article(article: dict, max_sentences: int = 2) -> str:
#     text = clean_text(article.get("content", "")) or clean_text(article.get("title", ""))
#     sentences = re.split(r"(?<=[.!?])\s+", text)
#     chosen = [sentence for sentence in sentences if sentence][:max_sentences]
#     if not chosen:
#         return clean_text(article.get("title", ""))
#     return " ".join(chosen)


# def summarize_dataset(articles: list[dict], topic: str) -> str:
#     if not articles:
#         return f"No significant {topic.lower()} articles found in the selected window."

#     sources = sorted({article.get("source", "Unknown") for article in articles})
#     return (
#         f"Collected {len(articles)} relevant {topic.lower()} articles from "
#         f"{', '.join(sources)} during the last 7 days."
#     )

import re
from collections import Counter
from typing import List, Dict, Tuple

from src.utils.text_utils import clean_text


def summarize_article(
    article: Dict,
    keywords: List[Tuple[str, int]] = None,
    max_sentences: int = 2,
) -> str:
    """
    Summarize a single article using keyword-aware sentence selection.
    Strategy:
    - Split into sentences
    - Score sentences by keyword presence
    - Prefer informative + keyword-rich sentences
    """
    text = clean_text(article.get("content", "")) or clean_text(article.get("title", ""))
    if not text:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return clean_text(article.get("title", ""))

    # Prepare keyword set
    keyword_set = set(k.lower() for k, _ in keywords) if keywords else set()

    def score_sentence(sentence: str) -> float:
        s = sentence.lower()
        keyword_hits = sum(1 for k in keyword_set if k in s)
        length_score = min(len(sentence) / 100, 1.0)  # normalize length
        return keyword_hits * 2 + length_score

    # Score and rank sentences
    ranked = sorted(sentences, key=score_sentence, reverse=True)

    # Take top sentences but preserve original order
    selected = sorted(ranked[:max_sentences], key=lambda s: sentences.index(s))

    return " ".join(selected)


def summarize_dataset(
    articles: List[Dict],
    topic: str,
    keywords: List[Tuple[str, int]],
    top_k_keywords: int = 5,
) -> str:
    """
    Generate an executive summary for the dataset.
    Strategy:
    - Use top keywords to identify main trends
    - Detect most common themes (coarse grouping)
    - Produce human-readable insight summary
    """
    if not articles:
        return f"No significant {topic.lower()} articles found in the selected window."

    # Extract top keywords
    top_keywords = [k for k, _ in keywords[:top_k_keywords]]
    keyword_str = ", ".join(top_keywords)

    # Count keyword occurrences across articles
    keyword_counter = Counter()
    for article in articles:
        text = f"{article.get('title', '')} {article.get('content', '')}".lower()
        for k in top_keywords:
            if k in text:
                keyword_counter[k] += 1

    # Identify dominant themes (top 2–3 keywords)
    dominant = [k for k, _ in keyword_counter.most_common(3)]

    # Source diversity (optional insight)
    sources = {article.get("source", "Unknown") for article in articles}

    # Build summary
    summary_parts = []

    # General overview
    summary_parts.append(
        f"In the past week, {topic.lower()} news has been dominated by topics such as {keyword_str}."
    )

    # Dominant trends
    if dominant:
        summary_parts.append(
            f"The most prominent themes include {', '.join(dominant)}, which appear frequently across multiple sources."
        )

    # Diversity / coverage insight
    summary_parts.append(
        f"The coverage spans {len(sources)} major news sources, reflecting a broad perspective on current developments."
    )

    # Optional: dynamic closing
    summary_parts.append(
        "Overall, the landscape highlights ongoing developments and emerging trends within the field."
    )

    return " ".join(summary_parts)