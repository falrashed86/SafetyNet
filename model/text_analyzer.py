import re
from functools import lru_cache

from transformers import pipeline

# ---------------------------------
# Minimal explicit override words
# Keep these only for obvious danger
# ---------------------------------
OVERRIDE_KEYWORDS = [
    "kill yourself",
    "suicide",
    "i want to die",
    "i will kill you",
    "bomb",
]

ARABIC_OVERRIDE_KEYWORDS = [
    "انتحار",
    "اقتل نفسك",
    "أقتل نفسك",
    "بقتل نفسي",
    "سأقتلك",
    "راح اقتلك",
]

# ---------------------------------
# Load multilingual sentiment model
# ---------------------------------
@lru_cache(maxsize=1)
def get_model():
    # multilingual: works for English + Arabic better than English-only models
    return pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment",
        tokenizer="nlptown/bert-base-multilingual-uncased-sentiment",
    )

# ---------------------------------
# Helpers
# ---------------------------------
def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def has_override(text: str) -> bool:
    t = normalize_text(text)

    for kw in OVERRIDE_KEYWORDS:
        if kw in t:
            return True

    for kw in ARABIC_OVERRIDE_KEYWORDS:
        if kw in text:
            return True

    return False


def parse_stars(label: str) -> int:
    # labels look like: "1 star", "2 stars", ...
    m = re.search(r"(\d)", label)
    if m:
        return int(m.group(1))
    return 3


def decide_risk_from_model(stars: int, confidence: float) -> str:
    """
    Model-driven risk mapping.
    This is what lets you show mode='model' in HIGH rows too.

    1 star  -> HIGH
    2 stars -> HIGH if confidence is strong enough, else MEDIUM
    3 stars -> MEDIUM
    4/5     -> LOW
    """
    if stars == 1:
        return "HIGH"
    if stars == 2:
        return "HIGH" if confidence >= 0.60 else "MEDIUM"
    if stars == 3:
        return "MEDIUM"
    return "LOW"


# ---------------------------------
# Main function
# ---------------------------------
def analyze_message(text: str) -> dict:
    original_text = text.strip()

    if not original_text:
        return {
            "text": "",
            "mode": "model",
            "stars": 3,
            "confidence": 0.0,
            "risk": "LOW",
        }

    # 1) Explicit keyword override
    if has_override(original_text):
        return {
            "text": original_text,
            "mode": "keyword_override",
            "stars": 1,
            "confidence": 1.0,
            "risk": "HIGH",
        }

    # 2) Model-based decision
    model = get_model()
    result = model(original_text)[0]

    label = result.get("label", "3 stars")
    confidence = float(result.get("score", 0.0))
    stars = parse_stars(label)
    risk = decide_risk_from_model(stars, confidence)

    return {
        "text": original_text,
        "mode": "model",
        "stars": stars,
        "confidence": round(confidence, 4),
        "risk": risk,
    }
