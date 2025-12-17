from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from my_app.models_Product import Product, ProductReview
# from sentiment.classifier import classify_comment

@require_POST
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

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

    # # Phân loại comment
    # result = classify_comment(comment)
    #
    # if result["is_spam"]:
    #     return JsonResponse({
    #         "success": False,
    #         "message": "Bình luận bị chặn do spam."
    #     })

    review = ProductReview.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
        # sentiment=result["sentiment"],  # 👈 thêm
        # is_spam=False,  # 👈 thêm
        approved=True
    )

    return JsonResponse({
        "success": True,
        "username": request.user.username,
        "rating": review.rating,
        "comment": review.comment,
        # "sentiment": review.sentiment,
        "created_at": review.created_at.strftime("%d/%m/%Y %H:%M")
    })

