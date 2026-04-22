from datetime import datetime, timezone
from pathlib import Path

from config.settings import Settings
from src.collectors.thanhnien import ThanhNienCollector
from src.collectors.tuoitre import TuoiTreCollector
from src.collectors.vnexpress import VnExpressCollector
from src.processors.filter import filter_articles
from src.processors.keyword_extractor import extract_top_keywords, rank_articles
from src.processors.summarizer import summarize_dataset
from src.utils.article_storage import load_articles_json, save_articles_json
from src.utils.date_utils import parse_iso_datetime
from src.utils.storage_paths import processed_article_path, raw_article_path


class NewsPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        self.collectors_map = {
            "VnExpress": VnExpressCollector(
                source_name="VnExpress",
                rss_url=self.settings.rss_sources["VnExpress"],
                max_items=self.settings.max_articles_per_source,
            ),
            "Thanh Nien": ThanhNienCollector(
                source_name="Thanh Nien",
                rss_url=self.settings.rss_sources["Thanh Nien"],
                max_items=self.settings.max_articles_per_source,
            ),
            "Tuoi Tre": TuoiTreCollector(
                source_name="Tuoi Tre",
                rss_url=self.settings.rss_sources["Tuoi Tre"],
                max_items=self.settings.max_articles_per_source,
            ),
        }

    def run(self) -> str:
        raw_dir = Path(self.settings.raw_data_dir)
        processed_dir = Path(self.settings.processed_data_dir)

        self._collect_and_save_raw_per_source(raw_dir)

        final_articles: list[dict] = []
        for source_name in self.collectors_map:
            raw_path = raw_article_path(raw_dir, source_name)
            source_articles = load_articles_json(raw_path)

            filtered = filter_articles(
                articles=source_articles,
                keywords=self.settings.filter_keywords,
                start_time=self.settings.time_window_start,
            )

            processed_for_source: list[dict] = []
            for article in filtered:
                collector = self._get_collector_by_source(
                    article.get("source") or article.get("source_name")
                )
                if collector:
                    full_text = collector.fetch_full_content(article["url"])
                    if full_text:
                        article = {**article, "content": full_text}
                    processed_for_source.append(article)

            out_path = processed_article_path(processed_dir, source_name)
            save_articles_json(out_path, processed_for_source)
            final_articles.extend(processed_for_source)

        keyword_weights = extract_top_keywords(
            final_articles, top_k=self.settings.top_keywords
        )
        keyword_ranked = sorted(
            keyword_weights.items(), key=lambda item: item[1], reverse=True
        )
        ranked_articles = rank_articles(final_articles, keyword_weights)
        highlights = ranked_articles[: self.settings.top_highlights]
        executive_summary = summarize_dataset(
            final_articles, self.settings.topic, keyword_ranked
        )

        return self._build_report(
            executive_summary=executive_summary,
            keywords=keyword_ranked,
            highlights=highlights,
        )

    def _collect_and_save_raw_per_source(self, raw_dir: Path) -> None:
        for source_name, collector in self.collectors_map.items():
            try:
                articles = collector.fetch_articles()
            except Exception as e:
                print(f"Error fetching from {source_name}: {e}")
                articles = []
            path = raw_article_path(raw_dir, source_name)
            save_articles_json(path, articles)

    def _get_collector_by_source(self, source_name: str | None):
        if not source_name:
            return None
        return self.collectors_map.get(source_name)

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
        keywords: list[tuple[str, float]],
        highlights: list[dict],
    ) -> str:
        keyword_lines = "\n".join(
            [f"- {keyword} ({count:.4f})" for keyword, count in keywords]
        )
        highlight_lines = "\n".join(
            [
                (
                    f"### {idx}. {article.get('title', 'Untitled')}\n"
                    f"- Source: {article.get('source_name') or article.get('source', 'Unknown')}\n"
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
