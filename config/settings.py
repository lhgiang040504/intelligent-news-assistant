from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


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
    "Technology": ["công nghệ", "ai", "blockchain", "phần mềm", "smartphone", "vi mạch", "số hóa", "tech", "điện tử"],
    "Sports": ["thể thao", "bóng đá", "v-league", "ngoại hạng anh", "tennis", "cầu lông", "vận động viên"],
    "Entertainment": ["giải trí", "showbiz", "nghệ sĩ", "phim", "nhạc", "concert", "hoa hậu", "điện ảnh"],
    "Fashion": ["thời trang", "bộ sưu tập", "runway", "người mẫu", "vogue", "tạp chí", "trang phục"]
}

@dataclass(frozen=True)
class Settings:
    topic: str
    days_back: int
    max_articles_per_source: int
    top_keywords: int
    top_highlights: int
    raw_data_dir: str
    processed_data_dir: str
    report_output_path: str

    @property
    def rss_sources(self) -> dict[str, str]:
        return TOPIC_TO_RSS[self.topic]

    @property
    def filter_keywords(self) -> list[str]:
        return TOPIC_KEYWORDS.get(self.topic, [self.topic.lower()])

    @property
    def time_window_start(self) -> datetime:
        return datetime.now(timezone.utc) - timedelta(days=self.days_back)

    @staticmethod
    def default() -> "Settings":
        return Settings(
            topic="Technology",
            days_back=7,
            max_articles_per_source=40,
            top_keywords=12,
            top_highlights=8,
            raw_data_dir=str(Path("data/raw")),
            processed_data_dir=str(Path("data/processed")),
            report_output_path=str(Path("reports/weekly_report.md")),
        )