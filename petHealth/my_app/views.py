from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from accounts.models import UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


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
from .services.recommendation import get_personal_recommendations


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

    liked_ids = []
    personal_products = Product.objects.none()
    if request.user.is_authenticated:
        liked_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

        # ✅ GỢI Ý CÁ NHÂN THẬT
        personal_products = get_personal_recommendations(
            request.user,
            limit=10
        )

    context = {
        'favorite_products': favorite_products,
        'sale_products': sale_products,
        'new_products': new_products,
        "personal_products": personal_products,
        "liked_ids": liked_ids,
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

    # Lấy tất cả promotion đang active
    promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related("products", "categories")

    # Tạo dict: promotion -> list products
    promo_products = {}
    
    for promo in promotions:
        products_set = set()
        
        # 1. Products gắn trực tiếp
        products_set.update(promo.products.all())
        
        # 2. Products theo categories
        for category in promo.categories.all():
            products_set.update(category.product_set.all())
        
        promo_products[promo] = list(products_set)

    return render(request, 'frontend/promotion.html', {
        "promo_products": promo_products,
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

from django.shortcuts import render, get_object_or_404
from .models_Product import Product, Category, Wishlist
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta


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
        products = products.order_by(
            "price",
            Case(
                When(expiry_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            "expiry_date"
        )
    elif sort == "price_desc":
        products = products.order_by(
            "-price",
            Case(
                When(expiry_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            "expiry_date"
        )
    else:
        # ✅ MẶC ĐỊNH: Sắp xếp theo BADGE (Khuyến mãi → New → Còn lại)
        products_list = list(products)

        promotion_products = []
        new_products = []
        other_products = []

        for p in products_list:
            if p.final_price != p.price:  # Có khuyến mãi
                promotion_products.append(p)
            elif p.expiry_date:  # Sản phẩm mới (có expiry_date)
                new_products.append(p)
            else:
                other_products.append(p)

        # Sắp xếp theo expiry_date trong từng nhóm
        promotion_products.sort(key=lambda x: x.expiry_date if x.expiry_date else timezone.now().date())
        new_products.sort(key=lambda x: x.expiry_date if x.expiry_date else timezone.now().date())
        other_products.sort(key=lambda x: x.expiry_date if x.expiry_date else timezone.now().date())

        # Ghép lại theo thứ tự: Khuyến mãi → New → Còn lại
        products_list = promotion_products + new_products + other_products
        products = products_list

    # ✅ Thêm thông tin về trạng thái hết hạn cho từng sản phẩm
    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)

    products_with_status = []

    # Xử lý cho cả queryset và list
    products_to_process = products if isinstance(products, list) else list(products)

    for product in products_to_process:
        product.is_expiring_soon = False
        product.is_expired = False
        product.days_until_expiry = None

        if product.expiry_date:
            product.days_until_expiry = (product.expiry_date - today).days

            if product.expiry_date < today:
                product.is_expired = True
            elif product.expiry_date <= thirty_days_later:
                product.is_expiring_soon = True

        products_with_status.append(product)

    # ===== LIKED IDS =====
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
        "products": products_with_status,
        "liked_ids": liked_ids,
        "selected_prices": selected_prices,
        "selected_brands": selected_brands,
        "sort": sort,
    })


from django.shortcuts import render, get_object_or_404
from .models_Product import Wishlist
# from sentiment.spam_filter import is_spam
from django.db.models import Avg, Count, Q
from orders.models import Order, OrderItem  # Hoặc đường dẫn đúng của model Order


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Lấy danh sách sản phẩm liên quan theo logic của model
    related = product.get_related_products(limit=10)

    # ✅ LẤY REVIEWS THEO review_group HOẶC slug
    # Nếu sản phẩm có review_group, lấy reviews của TẤT CẢ sản phẩm cùng group
    # Nếu không có review_group, chỉ lấy reviews của sản phẩm này
    review_identifier = product.get_review_identifier()
    
    if product.review_group:
        # Lấy tất cả sản phẩm cùng review_group
        products_in_group = Product.objects.filter(
            Q(review_group=review_identifier) | Q(slug=review_identifier)
        )
        # Lấy reviews của tất cả sản phẩm trong group
        from my_app.models_Product import ProductReview
        reviews = ProductReview.objects.filter(
            product__in=products_in_group,
            approved=True,
            is_spam=False
        )
    else:
        # Chỉ lấy reviews của sản phẩm hiện tại
        reviews = product.reviews.filter(approved=True, is_spam=False)

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

    # ✅ KIỂM TRA USER ĐÃ MUA SẢN PHẨM NÀY CHƯA
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status='delivered'  # Thay đổi status phù hợp với hệ thống của bạn
        ).exists()

    return render(request, "frontend/detailProduct.html", {
        "product": product,
        "related": related,
        "reviews": reviews,
        "liked_ids": liked_ids,
        "avg_rating": avg_rating,
        "total_reviews": total_reviews,
        "rating_counts": rating_counts,
        "commented_count": commented_count,
        "has_purchased": has_purchased,  # ✅ Thêm biến này
    })

from django.shortcuts import get_object_or_404, redirect
from .models_Product import Product, ProductSize

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    size_id = request.POST.get("size_id")
    quantity = int(request.POST.get("quantity", 1))

    cart = request.session.get("cart", {})

    # ====== TRƯỜNG HỢP CÓ SIZE ======
    if product.sizes.exists():
        if not size_id:
            return redirect("product_detail", slug=product.slug)

        size = get_object_or_404(ProductSize, id=size_id, product=product)

        final_price = size.get_final_price()
        cart_key = f"{product.id}_{size.id}"

        item_data = {
            "product_id": product.id,
            "size_id": size.id,
            "name": product.name,
            "size": size.size_name,
            "price": final_price,
            "image": product.image,
            "slug": product.slug,
            "quantity": quantity
        }

    # ====== TRƯỜNG HỢP KHÔNG CÓ SIZE ======
    else:
        final_price = product.final_price
        cart_key = str(product.id)

        item_data = {
            "product_id": product.id,
            "size_id": None,
            "name": product.name,
            "size": None,
            "price": final_price,
            "image": product.image,
            "slug": product.slug,
            "quantity": quantity
        }

    # ====== ADD / UPDATE CART ======
    if cart_key in cart:
        cart[cart_key]["quantity"] += quantity
    else:
        cart[cart_key] = item_data

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


def remove_cart(request, cart_key):
    cart = request.session.get("cart", {})

    if cart_key in cart:
        del cart[cart_key]
        request.session.modified = True

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
    sort = request.GET.get("sort", "")  # ✅ Thêm sort

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

    # ====== SORT ======
    if sort == "price_asc":
        # ✅ Ưu tiên GIÁ trước, nếu cùng giá thì ưu tiên hạn sử dụng
        products = products.order_by(
            "price",
            Case(
                When(expiry_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            "expiry_date"
        )
    elif sort == "price_desc":
        # ✅ Ưu tiên GIÁ trước, nếu cùng giá thì ưu tiên hạn sử dụng
        products = products.order_by(
            "-price",
            Case(
                When(expiry_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            "expiry_date"
        )
    else:
        # ✅ MẶC ĐỊNH: Ưu tiên hạn sử dụng
        products = products.order_by(
            Case(
                When(expiry_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            "expiry_date"
        )

    # ✅ Thêm thông tin về trạng thái hết hạn cho từng sản phẩm
    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)

    products_with_status = []
    for product in products:
        product.is_expiring_soon = False
        product.is_expired = False
        product.days_until_expiry = None

        if product.expiry_date:
            product.days_until_expiry = (product.expiry_date - today).days

            if product.expiry_date < today:
                product.is_expired = True
            elif product.expiry_date <= thirty_days_later:
                product.is_expiring_soon = True

        products_with_status.append(product)

    # ✅ Lấy liked_ids
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            Wishlist.objects.filter(user=request.user)
            .values_list("product_id", flat=True)
        )

    return render(request, "frontend/search.html", {
        "keyword": keyword_raw,
        "products": products_with_status,  # ✅ Đổi từ products
        "total": len(products_with_status),  # ✅ Đổi từ products.count()
        "selected_prices": selected_prices,
        "selected_brands": selected_brands,
        "sort": sort,  # ✅ Thêm sort
        "liked_ids": liked_ids,  # ✅ Thêm liked_ids
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
            return redirect('home')  # ✅ về HomePage
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


def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    orders = Order.objects.filter(user=user)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    delivered_orders = orders.filter(status="delivered")

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
        "delivered_orders": delivered_orders,
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
        return JsonResponse({"success": False, "message": "Invalid method"}, status=400)

    file = request.FILES.get("query_image")
    if not file:
        return JsonResponse({"success": False, "message": "No image"}, status=400)

    # extract feature
    query_feat = extract_feature_from_file(file, None).reshape(1, -1)

    # cosine similarity
    sims = cosine_similarity(query_feat, library_features)[0]

    idx = int(sims.argmax())
    best_score = float(sims[idx])

    SIM_THRESHOLD = 0.75

    # ❌ ẢNH KHÔNG HỢP LỆ
    if best_score < SIM_THRESHOLD:
        return JsonResponse({
            "success": False,
            "message": "Ảnh không hợp lệ hoặc không giống sản phẩm nào",
            "score": round(best_score, 3)
        })

    # ✅ ẢNH HỢP LỆ
    best_url = library_urls[idx]

    img = ProductImage.objects.filter(url=best_url).select_related("product").first()
    if not img:
        return JsonResponse({"success": False, "message": "Not found"}, status=404)

    return JsonResponse({
        "success": True,
        "url": f"/product/{img.product.slug}/",
        "score": round(best_score, 3)
    })



from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json


# @login_required
# @require_POST
# def checkout_from_cart(request):
#     data = json.loads(request.body)
#
#     # ✅ JS gửi { items: [{id, quantity}, ...] }
#     items = data.get("items", [])
#
#     cart = request.session.get("cart", {})
#     checkout_items = {}
#
#     for item in items:
#         pid = str(item.get("id"))
#         qty = int(item.get("quantity", 1))
#
#         if pid in cart:
#             checkout_items[pid] = cart[pid].copy()
#             checkout_items[pid]["quantity"] = qty  # ✅ lấy số lượng từ JS
#
#     # 👉 lưu vào session để trang shipping / payment dùng
#     request.session["checkout_items"] = checkout_items
#     request.session.modified = True
#
#     return JsonResponse({"ok": True})

from rag.rag1.rag_chain import load_rag_chain
# load RAG LAZY (chỉ load khi cần)
rag_chain = None


def get_rag_chain():
    global rag_chain
    if rag_chain is None:
        from rag.rag1.rag_chain import load_rag_chain
        rag_chain = load_rag_chain()
    return rag_chain


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8"))
        message = body.get("message", "").strip()
        if not message:
            return JsonResponse({"answer": "Bạn vui lòng nhập câu hỏi 🐾"})
        qa = get_rag_chain()
        result = qa.invoke({"query": message})
        return JsonResponse({"answer": result.get("result", "Mình chưa tìm được câu trả lời 😿")})
    except Exception as e:
        return JsonResponse({
            "answer": f"⚠️ Lỗi hệ thống: {str(e)}"
        }, status=500)

from django.utils import timezone

Product.objects.filter(expiry_date__gte=timezone.now().date())


from django.utils import timezone
from datetime import timedelta

def can_apply_promotion(product, promotion):
    # 1. Promotion còn hiệu lực?
    if not promotion.is_valid_now():
        return False

    # 2. Product có hạn sử dụng không?
    if not product.expiry_date:
        return False

    # 3. Product còn hạn (chưa hết hạn)
    return product.expiry_date >= timezone.now().date()

def trangChinhSachVanChuyen(request):
    return render(request, 'frontend/ChinhSachVanChuyen.html')

def trangChinhSachDoiTraHang(request):
    return render(request, 'frontend/ChinhSachDoiTraHang.html')

def trangLienHe(request):
    return render(request, 'frontend/LienHe.html')

def trangThanhToanTienLoi(request):
    return render(request, 'frontend/ThanhToanTienLoi.html')

def chinhSachKhuyenMai(request):
    return render(request, 'frontend/chinhSachKhuyenMai.html')

from django.shortcuts import render
from django.db.models import Q
from .models_Product import Product, Wishlist


def new_products_view(request):
    # Lấy tất cả sản phẩm
    products = Product.objects.all()

    # Lọc chỉ lấy sản phẩm mới
    new_products = [p for p in products if p.is_new_product()]

    # Lọc theo giá
    selected_prices = request.GET.getlist('price')
    if selected_prices:
        filtered = []
        for product in new_products:
            for price_range in selected_prices:
                min_price, max_price = map(int, price_range.split('-'))
                if min_price <= product.final_price <= max_price:
                    filtered.append(product)
                    break
        new_products = filtered

    # Lọc theo thương hiệu
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        new_products = [p for p in new_products if p.brand in selected_brands]

    # Lấy danh sách ID sản phẩm yêu thích
    liked_ids = []
    if request.user.is_authenticated:
        liked_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    context = {
        'products': new_products,
        'total': len(new_products),
        'selected_prices': selected_prices,
        'selected_brands': selected_brands,
        'liked_ids': liked_ids,
    }

    return render(request, 'frontend/newProduct.html', context)