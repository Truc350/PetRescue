from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from django.http import JsonResponse


# Create your views here.
def get_home(request):
    return render(request, 'home.html')  # tra ve trang my_app trong trang web


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


def getHomePage(request):
    return render(request, 'frontend/homePage.html')


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


def getPromotion(request):
    return render(request, 'frontend/promotion.html')


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
from .models_Product import Product, Category


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    return render(request, "frontend/DogKibbleView.html", {
        "category": category,
        "products": products
    })


from django.shortcuts import render, get_object_or_404
from .models_Product import Product, ProductReview


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Lấy danh sách sản phẩm liên quan theo logic của model
    related = product.get_related_products(limit=10)

    # Lấy review đã duyệt
    reviews = product.reviews.filter(approved=True)

    return render(request, "frontend/detailProduct.html", {
        "product": product,
        "related": related,
        "reviews": reviews,
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
