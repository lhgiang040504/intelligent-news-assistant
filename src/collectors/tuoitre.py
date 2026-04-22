import requests
from bs4 import BeautifulSoup
from src.collectors.rss_collector import RSSCollector

class TuoiTreCollector(RSSCollector):
    def fetch_full_content(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tuổi Trẻ thường dùng id main-detail-content hoặc class detail-cnd
            content_tag = soup.find('div', id='main-detail-content') or \
                          soup.find('div', class_='detail-cnd') or \
                          soup.find('div', class_='fck')
            
            if content_tag:
                return content_tag.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"Error scraping Tuoi Tre: {e}")
        return ""