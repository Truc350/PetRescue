from django.db.models import Q
from my_app.models_Product import Product, Wishlist
from orders.models import OrderItem


def get_personal_recommendations(user, limit=10):
    if not user.is_authenticated:
        return Product.objects.order_by("?")[:limit]

    # 1. Sản phẩm đã thích
    liked_products = Product.objects.filter(
        wishlisted_users__user=user
    )

    # 2. Sản phẩm đã mua
    bought_products = Product.objects.filter(
        orderitem__order__user=user
    )

    seed_products = (liked_products | bought_products).distinct()

    if not seed_products.exists():
        return Product.objects.order_by("?")[:limit]

    categories = seed_products.values_list("category", flat=True)
    brands = seed_products.values_list("brand", flat=True)

    # 3. Gợi ý
    recommended = Product.objects.filter(
        Q(category__in=categories) |
        Q(brand__in=brands)
    ).exclude(
        id__in=seed_products.values_list("id", flat=True)
    ).distinct()

    return recommended[:limit]
