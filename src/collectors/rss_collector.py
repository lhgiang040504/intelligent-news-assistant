from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from src.collectors.base_collector import BaseCollector
from src.utils.date_utils import to_utc
from src.utils.text_utils import clean_text


class RSSCollector(BaseCollector):
    def fetch_articles(
        self, min_published_after: datetime | None = None
    ) -> list[dict]:
        request = Request(self.rss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=20) as response:
            xml_data = response.read()

        root = ElementTree.fromstring(xml_data)
        items = root.findall(".//item")

        anchor = to_utc(min_published_after) if min_published_after is not None else None

        articles: list[dict] = []
        for item in items:
            title = clean_text(item.findtext("title", default=""))
            link = clean_text(item.findtext("link", default=""))
            description = clean_text(item.findtext("description", default=""))
            pub_date_raw = clean_text(item.findtext("pubDate", default=""))
            pub_date = self._parse_date(pub_date_raw)

            if not title or not link or pub_date is None:
                continue

            pub_utc = to_utc(pub_date)
            if anchor is not None and pub_utc <= anchor:
                break

            articles.append(
                {
                    "source": self.source_name,
                    "source_name": self.source_name,
                    "title": title,
                    "url": link,
                    "content": description,
                    "published_at": pub_utc.isoformat(),
                }
            )

            if len(articles) >= self.max_items:
                break

        return articles

    @staticmethod
    def _parse_date(value: str):
        if not value:
            return None
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=None)
            return dt
        except (TypeError, ValueError, IndexError):
            return None
