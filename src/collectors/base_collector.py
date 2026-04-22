from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


class BaseCollector(ABC):
    def __init__(self, source_name: str, rss_url: str, max_items: int = 30) -> None:
        self.source_name = source_name
        self.rss_url = rss_url
        self.max_items = max_items

    @abstractmethod
    def fetch_articles(self) -> list[dict]:
        """Return a list of article dictionaries."""
        pass
    
    @abstractmethod
    def fetch_full_content(self, url: str) -> str:
        pass