import hmac
import hashlib
from urllib.parse import urlencode, quote_plus
from datetime import datetime


def hmac_sha512(key, data):
    return hmac.new(
        key.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()


class VNPay:
    def __init__(self, tmn_code, hash_secret, payment_url, return_url):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.payment_url = payment_url
        self.return_url = return_url

    def get_client_ip(self, request):
        return request.META.get("REMOTE_ADDR", "127.0.0.1")

    def create_payment_url(self, request, order_id, amount, order_desc):
        vnp_params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": int(amount) * 100,
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": str(order_id),
            "vnp_OrderInfo": order_desc,
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": self.return_url,
            "vnp_IpAddr": self.get_client_ip(request),
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
        }

        # 1️⃣ Sort A–Z
        sorted_params = sorted(vnp_params.items())

        # 2️⃣ TẠO CHUỖI HASH (URL-ENCODE – CỰC KỲ QUAN TRỌNG)
        hash_data = urlencode(sorted_params, quote_via=quote_plus)

        # 3️⃣ Ký SHA512
        secure_hash = hmac_sha512(self.hash_secret, hash_data)

        # 4️⃣ Tạo URL thanh toán
        payment_url = (
            f"{self.payment_url}?"
            f"{hash_data}&vnp_SecureHash={secure_hash}"
        )

        return payment_url


def verify_vnpay_signature(params, hash_secret):
    vnp_secure_hash = params.pop("vnp_SecureHash", None)
    params.pop("vnp_SecureHashType", None)

    sorted_params = sorted(params.items())

    # ⚠️ PHẢI URL-ENCODE giống lúc gửi đi
    hash_data = urlencode(sorted_params, quote_via=quote_plus)

    calculated_hash = hmac_sha512(hash_secret, hash_data)

    return calculated_hash == vnp_secure_hash
