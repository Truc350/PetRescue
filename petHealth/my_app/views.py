from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from accounts.models import UserProfile
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
    return render(request, 'frontend/forgot_password.html')


def getPayment(request):
    return render(request, 'frontend/payment.html')


def getPaymentInfor(request):
    return render(request, 'frontend/delivery-infor.html')


def getCategory(request):
    return render(request, 'frontend/category.html')

def getSupport(request):
    return render(request, 'frontend/support.html')


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


from django.contrib.auth.decorators import login_required

@login_required
def getPersonal(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    return render(request, "frontend/personal-page.html", {
        "user_obj": user,
        "profile": profile
    })



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
# from sentiment.spam_filter import is_spam
from django.db.models import Avg, Count

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Lấy danh sách sản phẩm liên quan theo logic của model
    related = product.get_related_products(limit=10)

    # # Lấy review đã duyệt
    # reviews = product.reviews.filter(approved=True, is_spam=False)
    reviews = product.reviews.filter(approved=True)

    total_reviews = reviews.count()

    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0
    avg_rating = round(avg_rating, 1)

    rating_counts = {
        star: reviews.filter(rating=star).count()
        for star in range(1, 6)
    }

    commented_count = reviews.exclude(comment__isnull=True).exclude(comment="").count()

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
        "avg_rating": avg_rating,
        "total_reviews": total_reviews,
        "rating_counts": rating_counts,
        "commented_count": commented_count,
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
            "price": product.final_price,  # đúng model
            "image": product.image,
            "slug": product.slug,
            "quantity": quantity
        }

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("shoppingcart")


def shoppingcart(request):
    cart = request.session.get("cart", {})

    if request.method == "POST":
        pid = request.POST.get("product_id")
        action = request.POST.get("action")

        if pid in cart:
            if action == "increase":
                cart[pid]["quantity"] += 1
            elif action == "decrease":
                cart[pid]["quantity"] = max(1, cart[pid]["quantity"] - 1)

            request.session["cart"] = cart
            request.session.modified = True

        return redirect("shoppingcart")  # ⭐ RẤT QUAN TRỌNG

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

    selected_prices = request.GET.getlist("price")
    selected_brands = request.GET.getlist("brand")

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

    # ====== LỌC GIÁ (TRÊN KẾT QUẢ SEARCH) ======
    if selected_prices:
        price_q = Q()
        for p in selected_prices:
            min_price, max_price = p.split("-")
            price_q |= Q(
                price__gte=int(min_price),
                price__lte=int(max_price)
            )
        products = products.filter(price_q)

    # ====== LỌC BRAND (TRÊN KẾT QUẢ SEARCH) ======
    if selected_brands:
        products = products.filter(brand__in=selected_brands)

    return render(request, "frontend/search.html", {
        "keyword": keyword_raw,
        "products": products,
        "total": products.count(),
        "selected_prices": selected_prices,
        "selected_brands": selected_brands,
    })

# views.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')   # ✅ về HomePage
        else:
            return render(request, 'login.html', {
                'error': 'Sai tài khoản hoặc mật khẩu'
            })

    return render(request, 'login.html')

from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from orders.models import Order
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    orders = Order.objects.filter(user=user)

    gender_options = ["Nam", "Nữ", "Khác"]
    selected_gender = profile.gender or ""

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # ===== CẬP NHẬT HỒ SƠ =====
        if form_type == "profile":
            user.first_name = request.POST.get("first_name", "")
            user.last_name = request.POST.get("last_name", "")
            user.save()

            profile.phone = request.POST.get("phone", "")
            profile.gender = request.POST.get("gender", "")
            profile.birthday = request.POST.get("birthday") or None
            profile.save()

            messages.success(request, "Cập nhật hồ sơ thành công")
            return redirect("personal-page")

        # ===== ĐỔI MẬT KHẨU =====
        if form_type == "password":
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if not all([current_password, new_password, confirm_password]):
                messages.error(request, "Vui lòng nhập đầy đủ thông tin")
                return redirect("personal-page")

            if not user.check_password(current_password):
                messages.error(request, "Mật khẩu hiện tại không đúng")
                return redirect("personal-page")

            if new_password != confirm_password:
                messages.error(request, "Mật khẩu mới không khớp")
                return redirect("personal-page")

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            messages.success(request, "Đổi mật khẩu thành công")
            return redirect("personal-page")

    return render(request, "frontend/personal-page.html", {
        "user_obj": user,
        "profile": profile,
        "orders": orders,
        "gender_options": gender_options,
        "selected_gender": selected_gender
    })


from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models_Product import Product

@require_GET
def search_suggest(request):
    keyword = request.GET.get("q", "").strip()

    if not keyword:
        return JsonResponse([], safe=False)

    products = (
        Product.objects
        .filter(name__icontains=keyword)
        .values("name", "slug")[:8]
    )

    return JsonResponse(list(products), safe=False)


from sklearn.metrics.pairwise import cosine_similarity
from .services.image_index import library_features, library_urls
from .services.feature import extract_feature_from_file
from .services.yolo import yolo_model

def image_search(request):
    best_url = None
    best_score = None

    if request.method == "POST":
        query_feat = extract_feature_from_file(
            request.FILES["query_image"], yolo_model
        )

        sims = cosine_similarity([query_feat], library_features)[0]
        idx = sims.argmax()

        best_url = library_urls[idx]
        best_score = sims[idx]

    return render(request, "search.html", {
        "best_url": best_url,
        "best_score": best_score
    })
from django.http import JsonResponse
from sklearn.metrics.pairwise import cosine_similarity
from my_app.models_Product import ProductImage
from .services.image_index import library_features, library_urls
from .services.feature import extract_feature_from_file


def image_search_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    file = request.FILES.get("query_image")
    if not file:
        return JsonResponse({"error": "No image"}, status=400)

    # extract feature
    query_feat = extract_feature_from_file(file, None)
    query_feat = query_feat.reshape(1, -1)

    # cosine similarity
    sims = cosine_similarity(query_feat, library_features)[0]
    idx = int(sims.argmax())
    best_url = library_urls[idx]

    # tìm Product
    img = ProductImage.objects.filter(url=best_url).select_related("product").first()
    if not img:
        return JsonResponse({"error": "Not found"}, status=404)

    return JsonResponse({
        "url": f"/product/{img.product.slug}/",
        "score": float(sims[idx])
    })
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
@login_required
@require_POST
def checkout_from_cart(request):
    data = json.loads(request.body)

    # ✅ JS gửi { items: [{id, quantity}, ...] }
    items = data.get("items", [])

    cart = request.session.get("cart", {})
    checkout_items = {}

    for item in items:
        pid = str(item.get("id"))
        qty = int(item.get("quantity", 1))

        if pid in cart:
            checkout_items[pid] = cart[pid].copy()
            checkout_items[pid]["quantity"] = qty  # ✅ lấy số lượng từ JS

    # 👉 lưu vào session để trang shipping / payment dùng
    request.session["checkout_items"] = checkout_items
    request.session.modified = True

    return JsonResponse({"ok": True})

