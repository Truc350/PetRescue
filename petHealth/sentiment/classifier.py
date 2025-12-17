from .spam_filter import is_spam
from .ml_phobert import predict_sentiment

def classify_comment(text: str) -> dict:
    if is_spam(text):
        return {
            "is_spam": True,
            "sentiment": None
        }

    return {
        "is_spam": False,
        "sentiment": predict_sentiment(text)
    }
