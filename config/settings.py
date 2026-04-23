from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path


def _utc_start_of_day(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def _utc_end_of_day(d: date) -> datetime:
    return datetime.combine(d, time.max, tzinfo=timezone.utc)

TOPIC_TO_RSS = {
    "Technology": {
        "VnExpress": "https://vnexpress.net/rss/so-hoa.rss",
        "Thanh Nien": "https://thanhnien.vn/rss/cong-nghe.rss",
        "Tuoi Tre": "https://tuoitre.vn/rss/nhip-song-so.rss",
    },
    "Sports": {
        "VnExpress": "https://vnexpress.net/rss/the-thao.rss",
        "Thanh Nien": "https://thanhnien.vn/rss/the-thao.rss",
        "Tuoi Tre": "https://tuoitre.vn/rss/the-thao.rss",
    },
    "Entertainment": {
        "VnExpress": "https://vnexpress.net/rss/giai-tri.rss",
        "Thanh Nien": "https://thanhnien.vn/rss/giai-tri.rss",
        "Tuoi Tre": "https://tuoitre.vn/rss/giai-tri.rss",
    },
    "Fashion": {
        "VnExpress": "https://vnexpress.net/rss/thoi-trang.rss",
        "Thanh Nien": "https://thanhnien.vn/rss/thoi-trang-tre.rss",
        "Tuoi Tre": "https://tuoitre.vn/rss/thoi-trang.rss",
    },
}

TOPIC_KEYWORDS = {
    "Technology": [
        "công nghệ",
        "ai",
        "blockchain",
        "phần mềm",
        "smartphone",
        "vi mạch",
        "số hóa",
        "tech",
        "điện tử",
    ],
    "Sports": [
        "thể thao",
        "bóng đá",
        "v-league",
        "ngoại hạng anh",
        "tennis",
        "cầu lông",
        "vận động viên",
    ],
    "Entertainment": [
        "giải trí",
        "showbiz",
        "nghệ sĩ",
        "phim",
        "nhạc",
        "concert",
        "hoa hậu",
        "điện ảnh",
    ],
    "Fashion": [
        "thời trang",
        "bộ sưu tập",
        "runway",
        "người mẫu",
        "vogue",
        "tạp chí",
        "trang phục",
    ],
}


def _canonical_topic_key(user_topic: str) -> str | None:
    t = user_topic.strip()
    for key in TOPIC_TO_RSS:
        if key.lower() == t.lower():
            return key
    return None


def _resolve_rss_topic_key(user_topic: str) -> str:
    return _canonical_topic_key(user_topic) or "Technology"


def _build_filter_keywords(user_topic: str, rss_topic_key: str) -> list[str]:
    if _canonical_topic_key(user_topic) is not None:
        return list(TOPIC_KEYWORDS.get(rss_topic_key, [rss_topic_key.lower()]))

    custom = user_topic.strip().lower()
    base = list(TOPIC_KEYWORDS.get(rss_topic_key, []))
    if custom and custom not in base:
        return [custom] + base
    return base


@dataclass(frozen=True)
class Settings:
    """User-facing topic label + RSS map key + absolute UTC time window."""

    topic: str
    rss_topic_key: str
    filter_keywords: list[str]
    window_start: datetime
    window_end: datetime
    rolling_days: int | None
    max_articles_per_source: int
    top_keywords: int
    top_highlights: int
    raw_data_dir: str
    processed_data_dir: str
    report_output_path: str

    @property
    def rss_sources(self) -> dict[str, str]:
        return TOPIC_TO_RSS[self.rss_topic_key]

    @property
    def time_window_start(self) -> datetime:
        return self.window_start

    @property
    def time_window_end(self) -> datetime:
        return self.window_end

    def window_label(self) -> str:
        if self.rolling_days is not None:
            return f"last {self.rolling_days} day(s) ending {self.window_end.strftime('%Y-%m-%d %H:%M UTC')}"
        return (
            f"{self.window_start.date().isoformat()} to {self.window_end.date().isoformat()} (UTC, inclusive)"
        )

    @staticmethod
    def default() -> "Settings":
        return Settings.from_inputs(topic="technology", days=7, date_from=None, date_to=None)

    @staticmethod
    def from_inputs(
        *,
        topic: str,
        days: int,
        date_from: date | None,
        date_to: date | None,
        max_articles_per_source: int = 40,
        top_keywords: int = 12,
        top_highlights: int = 8,
        raw_data_dir: str | None = None,
        processed_data_dir: str | None = None,
        report_output_path: str | None = None,
    ) -> "Settings":
        now = datetime.now(timezone.utc)
        if date_from is not None and date_to is not None:
            window_start = _utc_start_of_day(date_from)
            window_end = _utc_end_of_day(date_to)
            rolling_days = None
            if window_start > window_end:
                raise ValueError("--from must be on or before --to")
        else:
            if days < 1:
                raise ValueError("--days must be at least 1")
            window_end = now
            window_start = now - timedelta(days=days)
            rolling_days = days

        rss_key = _resolve_rss_topic_key(topic)
        display = (topic.strip() or rss_key)
        keywords = _build_filter_keywords(topic, rss_key)

        return Settings(
            topic=display,
            rss_topic_key=rss_key,
            filter_keywords=keywords,
            window_start=window_start,
            window_end=window_end,
            rolling_days=rolling_days,
            max_articles_per_source=max_articles_per_source,
            top_keywords=top_keywords,
            top_highlights=top_highlights,
            raw_data_dir=raw_data_dir or str(Path("data/raw")),
            processed_data_dir=processed_data_dir or str(Path("data/processed")),
            report_output_path=report_output_path
            or str(
                Path("reports")
                / f"weekly_report_{now.strftime('%Y-%m-%d_%H%M%S')}_UTC.md"
            ),
        )
