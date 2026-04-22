# from collections import Counter

# from src.utils.text_utils import tokenize


# def extract_top_keywords(articles: list[dict], top_k: int = 10) -> list[tuple[str, int]]:
#     token_counter: Counter[str] = Counter()
#     for article in articles:
#         text = f"{article.get('title', '')} {article.get('content', '')}"
#         token_counter.update(tokenize(text))
#     return token_counter.most_common(top_k)
import math
from collections import Counter
from src.utils.text_utils import tokenize

def extract_top_keywords(articles: list[dict], top_k: int = 10) -> dict[str, float]:
    num_docs = len(articles)
    if num_docs == 0:
        return {}

    # 1. Tính TF cho từng bài và thống kê Document Frequency (DF)
    all_article_tokens = []
    df_counter = Counter()

    for article in articles:
        text = f"{article.get('title', '')} {article.get('content', '')}"
        tokens = tokenize(text)
        all_article_tokens.append(Counter(tokens))
        # Mỗi từ chỉ tính 1 lần cho DF trong 1 bài viết
        for word in set(tokens):
            df_counter[word] += 1

    # 2. Tính TF-IDF tổng thể để tìm ra Top Keywords của cả cụm bài viết
    tfidf_totals = Counter()
    for article_tokens in all_article_tokens:
        for word, count in article_tokens.items():
            tf = count / sum(article_tokens.values())
            idf = math.log(num_docs / (1 + df_counter[word]))
            tfidf_totals[word] += tf * idf

    # Trả về dict {keyword: weight}
    return dict(tfidf_totals.most_common(top_k))

def rank_articles(articles: list[dict], keyword_weights: dict[str, float]):
    ranked_results = []
    
    for article in articles:
        text = f"{article.get('title', '')} {article.get('content', '')}"
        tokens = set(tokenize(text)) # Dùng set để check tồn tại nhanh hơn
        
        # Tính điểm Score dựa trên tổng trọng số của các từ khóa xuất hiện
        # score = sum(weight cho mỗi keyword xuất hiện trong bài)
        score = sum(weight for word, weight in keyword_weights.items() if word in tokens)
        
        ranked_results.append({
            **article,
            "relevance_score": score
        })
        
    # Sắp xếp bài viết theo score cao nhất
    return sorted(ranked_results, key=lambda x: x['relevance_score'], reverse=True)