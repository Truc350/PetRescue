from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from django.http import JsonResponse


def getChatWithAI(request):
    return render(request, 'frontend/chatWithAI.html')


def getFooter(request):
    return render(request, 'frontend/footer.html')


def getHeader(request):
    return render(request, 'frontend/header.html')


def getLogin(request):
    return render(request, 'frontend/login.html')


def getRegister(request):
    return render(request, 'frontend/register.html')


def getForgotPassword(request):
    return render(request, 'frontend/forgot-password.html')


def getPayment(request):
    return render(request, 'frontend/payment.html')


def getPaymentInfor(request):
    return render(request, 'frontend/delivery-infor.html')


def getCategory(request):
    return render(request, 'frontend/category.html')


def getCategoryManage(request):
    return render(request, 'frontend/admin/category-manage.html')


def getCustomerManage(request):
    return render(request, 'frontend/admin/customer-manage.html')


def getProductManagement(request):
    return render(request, 'frontend/admin/product-management.html')


def getProfileAdmin(request):
    return render(request, 'frontend/admin/profileAdmin.html')


def getDogKibbleView(request):
    return render(request, 'frontend/DogKibbleView.html')


def getPersonal(request):
    return render(request, 'frontend/personal-page.html')


from django.shortcuts import render
from .models_Product import Product
from django.db import models
from django.db.models import Count


def getHomePage(request):
    favorite_products = (
        Product.objects
        .annotate(wishlist_count=Count("wishlisted_users"))
        .order_by("-wishlist_count")[:10]
    )

    sale_products = Product.objects.filter(
        discount_price__isnull=False
    ).order_by('-discount_price')[:10]

    new_products = Product.objects.all().order_by('-id')[:10]

    context = {
        'favorite_products': favorite_products,
        'sale_products': sale_products,
        'new_products': new_products,
    }

    return render(request, 'frontend/homePage.html', context)


def getDashBoard(request):
    return render(request, 'frontend/admin/dashboard.html')


def getHealthDog(request):
    return render(request, 'frontend/health-dog.html')


def getPolicy(request):
    return render(request, 'frontend/policy-purchases.html')


def getCatFood(request):
    return render(request, 'frontend/cat-food.html')


def getHealthCat(request):
    return render(request, 'frontend/health-cat.html')


def getCatToilet(request):
    return render(request, 'frontend/cat-toilet.html')


from django.utils import timezone
from .models_Product import Promotion


def getPromotion(request):
    now = timezone.now()

    promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related("products", "categories")

    products = Product.objects.filter(
        promotions__in=promotions
    ).distinct()

    return render(request, 'frontend/promotion.html', {
        "promotions": promotions,
        "products": products,
    })


def getDetailProduct(request):
    return render(request, 'frontend/detailProduct.html')


def getPromotionManage(request):
    return render(request, 'frontend/admin/promotion-manage.html')


def getStatistic(request):
    return render(request, 'frontend/admin/statistics.html')


def getDogHygiene(request):
    return render(request, 'frontend/dogHygiene.html')


def wishlist(request):
    return render(request, 'frontend/wishlist.html')


from django.shortcuts import render, get_object_or_404
from .models_Product import Product, Category, Wishlist
from django.db.models import Q


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    selected_prices = request.GET.getlist("price")
    selected_brands = request.GET.getlist("brand")
    sort = request.GET.get("sort", "")

    # ===== LỌC GIÁ =====
    if selected_prices:
        price_q = Q()
        for p in selected_prices:
            min_price, max_price = p.split("-")
            price_q |= Q(
                price__gte=int(min_price),
                price__lte=int(max_price)
            )
        products = products.filter(price_q)

    # ===== LỌC BRAND =====
    if selected_brands:
        products = products.filter(brand__in=selected_brands)

    # ===== SORT =====
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")

    if request.user.is_authenticated:
        liked_ids = set(
            Wishlist.objects.filter(
                user=request.user
            ).values_list("product_id", flat=True)
        )
    else:
        liked_ids = set()

    return render(request, "frontend/DogKibbleView.html", {
        "category": category,
        "products": products,
        "liked_ids": liked_ids,
        "selected_prices": selected_prices,
        "selected_brands": selected_brands,
        "sort": sort,
    })


from django.shortcuts import render, get_object_or_404
from .models_Product import Wishlist
from sentiment.spam_filter import is_spam

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Lấy danh sách sản phẩm liên quan theo logic của model
    related = product.get_related_products(limit=10)

    # Lấy review đã duyệt
    reviews = product.reviews.filter(approved=True, is_spam=False)

    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            Wishlist.objects.filter(user=request.user)
            .values_list("product_id", flat=True)
        )

    return render(request, "frontend/detailProduct.html", {
        "product": product,
        "related": related,
        "reviews": reviews,
        "liked_ids": liked_ids,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))

    cart = request.session.get("cart", {})

    pid = str(product.id)

    if pid in cart:
        cart[pid]["quantity"] += quantity
    else:
        cart[pid] = {
            "name": product.name,
            "price": product.final_price(),  # đúng model
            "image": product.image,
            "slug": product.slug,
            "quantity": quantity
        }

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("shoppingcart")


def shoppingcart(request):
    cart = request.session.get("cart", {})
    total = sum(
        item["price"] * item["quantity"]
        for item in cart.values()
    )

    return render(request, "frontend/shoppingcart.html", {
        "cart": cart,
        "total": total
    })


def remove_cart(request, product_id):
    cart = request.session.get("cart", {})
    pid = str(product_id)

    if pid in cart:
        del cart[pid]
        request.session["cart"] = cart

    return redirect("shoppingcart")


def remove_multiple_cart(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    data = json.loads(request.body)
    cart = request.session.get("cart", {})

    for pid in data.get("ids", []):
        cart.pop(str(pid), None)

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({"success": True})


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def toggle_wishlist_ajax(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            item.delete()
            return JsonResponse({"liked": False})

        return JsonResponse({"liked": True})

    return JsonResponse({"error": "Invalid request"}, status=400)


from django.contrib.auth.decorators import login_required


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product")

    return render(request, "frontend/wishlist.html", {
        "wishlist_items": wishlist_items
    })


@login_required
def remove_from_wishlist(request, product_id):
    if request.method == "POST":
        Wishlist.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()

    return redirect("wishlist")


from django.db.models import Q
from .models_Product import Product


def search_view(request):
    keyword_raw = request.GET.get("q", "").strip()
    keyword = keyword_raw.lower()

    products = Product.objects.none()

    # ====== TẦNG 1: HIỂU Ý (NHẸ – KHÔNG ÉP) ======
    ANIMAL_MAP = {
        "chó": "cho",
        "cho": "cho",
        "mèo": "meo",
        "meo": "meo",
    }

    TYPE_MAP = {
        "thức ăn": ["pate", "hạt"],
        "pate": ["pate"],
        "hạt": ["hạt"],
        "vệ sinh": ["cát", "sữa tắm", "kem đánh răng"],
        "sữa tắm": ["sữa tắm"],
        "cát": ["cát"],
    }

    animal = None
    types = []

    for k, v in ANIMAL_MAP.items():
        if k in keyword:
            animal = v
            break

    for k, v in TYPE_MAP.items():
        if k in keyword:
            types = v
            break

    query = Q()

    # ====== TẦNG 2: SEARCH MỀM ======
    if animal:
        query &= Q(category__slug__icontains=animal)

    if types:
        type_query = Q()
        for t in types:
            type_query |= Q(name__icontains=t)
            type_query |= Q(category__name__icontains=t)
        query &= type_query

    # ====== TẦNG 3: CỨU VỚT ======
    if not query:
        query = (
                Q(name__icontains=keyword_raw) |
                Q(brand__icontains=keyword_raw) |
                Q(category__name__icontains=keyword_raw) |
                Q(description__icontains=keyword_raw)
        )

    products = Product.objects.filter(query).distinct()

    return render(request, "frontend/search.html", {
        "keyword": keyword_raw,
        "products": products,
        "total": products.count(),
    })
