import requests
from bs4 import BeautifulSoup
from src.collectors.rss_collector import RSSCollector

class VnExpressCollector(RSSCollector):
    def fetch_full_content(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # VnExpress thường dùng tag article với class fck_detail
            content_tag = soup.find('article', class_='fck_detail')
            if not content_tag:
                content_tag = soup.find('div', class_='content-detail')
                
            if content_tag:
                # Loại bỏ các thành phần thừa như quảng cáo trong bài
                for hidden in content_tag(['script', 'style', 'div.insert-link']):
                    hidden.decompose()
                return content_tag.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"Error scraping VnExpress: {e}")
        return ""