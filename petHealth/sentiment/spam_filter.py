import re

spam_keywords = [
    # Mua bán
    "mua ngay", "mua liền", "đặt hàng", "chốt đơn",
    "giảm giá", "sale", "sale off", "khuyến mãi",
    "xả kho", "ưu đãi", "giá sốc", "giá rẻ",

    # Liên hệ
    "liên hệ", "ib", "inbox",
    "zalo", "facebook", "fb", "messenger",
    "hotline", "sđt", "số điện thoại",

    # Link
    "http", "https", "www", ".com", ".vn", ".net",

    # Spam phổ biến
    "cam kết", "100%", "uy tín",
    "kiếm tiền", "làm giàu",
    "cơ hội", "thu nhập",
    "nhận ngay", "free"
]

def is_spam(text):
    text = text.lower()

    if any(k in text for k in spam_keywords):
        return True

    if re.search(r"\d{9,11}", text):
        return True

    return False
