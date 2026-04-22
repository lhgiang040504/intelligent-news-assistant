import requests
from bs4 import BeautifulSoup
from src.collectors.rss_collector import RSSCollector

class ThanhNienCollector(RSSCollector):
    def fetch_full_content(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Thanh Niên thường dùng class detail-content hoặc id vne_content
            content_tag = soup.find('div', class_='detail-content') or \
                          soup.find('div', id='vne_content') or \
                          soup.find('div', class_='cms-body')
            
            if content_tag:
                return content_tag.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"Error scraping Thanh Nien: {e}")
        return ""