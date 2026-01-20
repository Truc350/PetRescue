from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from my_app.models_Product import Product, ProductReview
from sentiment.classifier import classify_comment
from orders.models import Order, OrderItem
from django.db.models import Q, Avg


@require_POST
@login_required
def add_review(request, slug):
    # Dùng slug cụ thể của sản phẩm để tránh MultipleObjectsReturned
    product = get_object_or_404(Product, slug=slug)

    # ✅ KIỂM TRA ĐÃ MUA HÀNG CHƯA
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status='delivered'  # Thay 'completed' bằng status đơn hàng hoàn thành của bạn
    ).exists()

    if not has_purchased:
        return JsonResponse({
            "success": False,
            "message": "Bạn cần mua sản phẩm này trước khi đánh giá!"
        })

    rating = request.POST.get("rating")
    comment = request.POST.get("comment")

    if not rating or not comment:
        return JsonResponse({
            "success": False,
            "message": "Thiếu dữ liệu đánh giá."
        })

    rating = int(rating)

    # Chặn đánh giá trùng
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        return JsonResponse({
            "success": False,
            "message": "Bạn đã đánh giá sản phẩm này rồi."
        })

    # Phân loại comment
    result = classify_comment(comment)

    if result["is_spam"]:
        return JsonResponse({
            "success": False,
            "message": "Bình luận bị chặn do spam."
        })

    review = ProductReview.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
        sentiment=result["sentiment"],
        is_spam=False,
        approved=True
    )

    return JsonResponse({
        "success": True,
        "username": request.user.username,
        "rating": review.rating,
        "comment": review.comment,
        "sentiment": review.sentiment,
        "created_at": review.created_at.strftime("%d/%m/%Y %H:%M")
    })

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from my_app.models_Product import Product, ProductReview
from io import BytesIO


def get_product_conclusion(positive, negative):
    total = positive + negative

    if total == 0:
        return "Hiện chưa có đủ đánh giá để đưa ra khuyến nghị mua sản phẩm này."

    ratio = positive / total

    if ratio >= 0.7:
        return "Sản phẩm được đánh giá rất tốt, bạn hoàn toàn có thể yên tâm lựa chọn."
    elif ratio >= 0.4:
        return "Sản phẩm nhận được phản hồi khá ổn, bạn vẫn có thể cân nhắc mua."
    else:
        return "Sản phẩm đang nhận nhiều phản hồi chưa tích cực, bạn nên cân nhắc kỹ trước khi mua."

def sentiment_chart(request, slug):
    # Aggregate reviews for the entire group or specific product
    reviews_qs = ProductReview.objects.filter(
        Q(product__review_group=slug) | Q(product__slug=slug),
        approved=True,
        is_spam=False
    )

    positive_count = reviews_qs.filter(sentiment="tích cực").count()
    negative_count = reviews_qs.filter(sentiment="tiêu cực").count()

    labels = ["Tích cực", "Tiêu cực"]
    values = [positive_count, negative_count]
    colors = ["#28a745", "#dc3545"]  # xanh lá – đỏ

    conclusion = get_product_conclusion(positive_count, negative_count)

    # ===== TẠO BIỂU ĐỒ =====
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # BIỂU ĐỒ CỘT
    axes[0].bar(labels, values, color=colors)
    axes[0].set_title("Biểu đồ cột")
    axes[0].set_ylabel("Số lượt đánh giá")

    for i, v in enumerate(values):
        axes[0].text(i, v + 0.05, str(v), ha="center", fontweight="bold")

    # BIỂU ĐỒ TRÒN
    if sum(values) > 0:
        axes[1].pie(
            values,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90
        )
        axes[1].axis("equal")
    else:
        axes[1].text(0.5, 0.5, "Chưa có đánh giá",
                     ha="center", va="center")

    axes[1].set_title("Tỷ lệ đánh giá")

    # ===== GHI KẾT LUẬN LÊN ẢNH =====
    fig.suptitle(conclusion, fontsize=14, fontweight="bold")

    # ===== TRẢ ẢNH =====
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from my_app.models_Product import Product, ProductReview

def sentiment_summary(request, slug):
    # Aggregate reviews for the entire group or specific product
    reviews_qs = ProductReview.objects.filter(
        Q(product__review_group=slug) | Q(product__slug=slug),
        approved=True,
        is_spam=False
    )

    positive_count = reviews_qs.filter(sentiment="tích cực").count()
    negative_count = reviews_qs.filter(sentiment="tiêu cực").count()

    total = positive_count + negative_count
    if total == 0:
        text = "Hiện chưa có đủ đánh giá để đưa ra kết luận."
    else:
        positive_percent = round(positive_count / total * 100)
        negative_percent = 100 - positive_percent
        text = f"{positive_percent}% người dùng cảm thấy tích cực và {negative_percent}% người dùng cảm thấy tiêu cực"

    return HttpResponse(text)

