import json
from datetime import datetime, timezone
from pathlib import Path

from config.settings import Settings
from src.collectors.thanhnien import ThanhNienCollector
from src.collectors.tuoitre import TuoiTreCollector
from src.collectors.vnexpress import VnExpressCollector
from src.processors.filter import filter_articles
from src.processors.keyword_extractor import extract_top_keywords
from src.processors.summarizer import summarize_dataset
from src.utils.date_utils import parse_iso_datetime


class NewsPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self) -> str:
        articles = self._collect_articles()
        self._save_json(self.settings.raw_data_path, articles)

        filtered_articles = filter_articles(
            articles=articles,
            topic=self.settings.topic,
            start_time=self.settings.time_window_start,
        )
        self._save_json(self.settings.processed_data_path, filtered_articles)

        keywords = extract_top_keywords(
            filtered_articles, top_k=self.settings.top_keywords
        )
        ranked_articles = self._rank_articles(filtered_articles, keywords)
        highlights = ranked_articles[: self.settings.top_highlights]
        executive_summary = summarize_dataset(filtered_articles, self.settings.topic)

        return self._build_report(
            executive_summary=executive_summary,
            keywords=keywords,
            highlights=highlights,
        )

    def _collect_articles(self) -> list[dict]:
        collectors = [
            VnExpressCollector(
                source_name="VnExpress",
                rss_url=self.settings.rss_sources["VnExpress"],
                max_items=self.settings.max_articles_per_source,
            ),
            ThanhNienCollector(
                source_name="Thanh Nien",
                rss_url=self.settings.rss_sources["Thanh Nien"],
                max_items=self.settings.max_articles_per_source,
            ),
            TuoiTreCollector(
                source_name="Tuoi Tre",
                rss_url=self.settings.rss_sources["Tuoi Tre"],
                max_items=self.settings.max_articles_per_source,
            ),
        ]

        articles: list[dict] = []
        for collector in collectors:
            try:
                articles.extend(collector.fetch_articles())
            except Exception:
                # Keep pipeline resilient when one source is temporarily unavailable.
                continue
        return articles

    def _rank_articles(
        self, articles: list[dict], keywords: list[tuple[str, int]]
    ) -> list[dict]:
        keyword_set = {keyword for keyword, _ in keywords}

        def score(article: dict) -> float:
            text = f"{article.get('title', '')} {article.get('content', '')}".lower()
            keyword_hits = sum(1 for keyword in keyword_set if keyword in text)
            published = parse_iso_datetime(article.get("published_at", ""))
            recency = 0.0
            if published:
                age_hours = max(
                    (datetime.now(timezone.utc) - published).total_seconds() / 3600, 1
                )
                recency = 1 / age_hours
            return keyword_hits * 2 + recency

        sorted_articles = sorted(articles, key=score, reverse=True)
        return [
            {
                **article,
                "summary": self._short_summary(article),
            }
            for article in sorted_articles
        ]

    def _short_summary(self, article: dict) -> str:
        content = (article.get("content") or "").strip()
        if not content:
            return article.get("title", "")
        return content[:260].rstrip() + ("..." if len(content) > 260 else "")

    def _build_report(
        self,
        executive_summary: str,
        keywords: list[tuple[str, int]],
        highlights: list[dict],
    ) -> str:
        keyword_lines = "\n".join(
            [f"- {keyword} ({count})" for keyword, count in keywords]
        )
        highlight_lines = "\n".join(
            [
                (
                    f"### {idx}. {article.get('title', 'Untitled')}\n"
                    f"- Source: {article.get('source', 'Unknown')}\n"
                    f"- Published: {article.get('published_at', 'N/A')}\n"
                    f"- Summary: {article.get('summary', '')}\n"
                    f"- Link: {article.get('url', '')}\n"
                )
                for idx, article in enumerate(highlights, start=1)
            ]
        )
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return (
            f"# Weekly News Report - {self.settings.topic}\n\n"
            f"Generated at: {now}\n\n"
            "## Executive Summary\n"
            f"{executive_summary}\n\n"
            "## Trending Keywords\n"
            f"{keyword_lines if keyword_lines else '- No keywords extracted'}\n\n"
            "## Highlighted News\n"
            f"{highlight_lines if highlight_lines else 'No highlighted articles.'}\n"
        )

    @staticmethod
    def _save_json(path_str: str, payload: list[dict]) -> None:
        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
