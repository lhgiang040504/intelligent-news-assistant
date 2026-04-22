import re
import unicodedata


VI_STOPWORDS = {
    "và",
    "là",
    "của",
    "cho",
    "trong",
    "với",
    "một",
    "những",
    "được",
    "đang",
    "các",
    "theo",
    "khi",
    "tại",
    "đã",
    "sẽ",
    "về",
    "này",
    "đó",
    "it",
    "its",
    "the",
    "a",
    "an",
    "to",
    "of",
    "in",
    "for",
}


def clean_text(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value or "")
    no_tags = re.sub(r"<[^>]+>", " ", normalized)
    return re.sub(r"\s+", " ", no_tags).strip()


def tokenize(value: str) -> list[str]:
    text = clean_text(value).lower()
    words = re.findall(r"[0-9a-zA-ZÀ-ỹ]{3,}", text)
    return [word for word in words if word not in VI_STOPWORDS]
