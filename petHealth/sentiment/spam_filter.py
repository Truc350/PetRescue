import re

spam_keywords = [
    "mua ngay", "giảm giá", "sale", "khuyến mãi",
    "liên hệ", "zalo", "facebook", "http", "www"
]

def is_spam(text):
    text = text.lower()

    if any(k in text for k in spam_keywords):
        return True

    if re.search(r"\d{9,11}", text):
        return True

    return False
