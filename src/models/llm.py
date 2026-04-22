from src.processors.summarizer import summarize_article


class LLMWrapper:
    """
    Stub wrapper for future API-based summarization.
    Currently delegates to local heuristic summarizer.
    """

    @staticmethod
    def summarize(article: dict) -> str:
        return summarize_article(article)
