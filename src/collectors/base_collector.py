from abc import ABC, abstractmethod
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class BaseCollector(ABC):
    def __init__(self, source_name: str, rss_url: str, max_items: int = 30) -> None:
        self.source_name = source_name
        self.rss_url = rss_url
        self.max_items = max_items

    @abstractmethod
    def fetch_articles(
        self, min_published_after: datetime | None = None
    ) -> list[dict]:
        """Return article dicts. If min_published_after is set, stop at older/equal items (RSS newest-first)."""
        pass
    
    @abstractmethod
    def fetch_full_content(self, url: str) -> str:
        pass