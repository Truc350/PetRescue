from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, ShippingAddress

@login_required
def checkout_shipping(request):
    order_id = request.session.get('checkout_order_id')

    if not order_id:
        # Nếu không có order trong session → redirect về buy_now hoặc giỏ hàng
        return redirect("orders:cart_view")  # thay cart_view bằng view giỏ hàng của bạn

    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related("product")
    total = sum(item.price * item.quantity for item in items)

    if request.method == "POST":
        ShippingAddress.objects.update_or_create(
            order=order,
            defaults={
                "full_name": request.POST["full_name"],
                "phone": request.POST["phone"],
                "address": request.POST["address"],
                "province": request.POST["province"],
                "ward": request.POST["ward"],
                "note": request.POST.get("note", ""),
            }
        )

        order.status = "pending"
        order.save()

        return redirect("orders:checkout_payment")

    return render(request, "frontend/delivery-infor.html", {
        "order": order,
        "items": items,
        "total": total,
        "saved_addresses": [],
    })

from django.shortcuts import get_object_or_404
from my_app.models_Product import Product
from .models import Order, OrderItem

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Xóa cart cũ nếu có
    Order.objects.filter(user=request.user, status="cart").delete()

    # Tạo order mới
    order = Order.objects.create(user=request.user, status="cart")

    # Thêm sản phẩm vào order
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )

    # Lưu order.id vào session
    request.session['checkout_order_id'] = order.id

    return redirect("orders:checkout_shipping")

import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse

@require_POST
def save_checkout_items(request):
    data = json.loads(request.body)
    ids = data.get("ids", [])

    request.session["checkout_product_ids"] = ids
    request.session.modified = True

    return JsonResponse({"ok": True})

from my_app.models_Product import Product

def delivery_info(request):
    ids = request.session.get("checkout_product_ids", [])
    products = Product.objects.filter(id__in=ids)

    return render(request, "frontend/delivery-infor.html", {
        "products": products
    })

from my_app.models_Product import Product

class CheckoutItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity
        self.subtotal = product.price * quantity


@login_required
def delivery_info(request):
    cart = request.session.get("cart", {})
    selected_ids = request.session.get("checkout_product_ids", [])

    items = []

    for pid in selected_ids:
        pid = str(pid)
        if pid in cart:
            product = Product.objects.get(id=pid)
            quantity = cart[pid]["quantity"]
            items.append(CheckoutItem(product, quantity))

    total = sum(item.subtotal for item in items)

    return render(request, "frontend/delivery-infor.html", {
        "items": items,
        "total": total
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def checkout_payment(request):
    order_id = request.session.get('checkout_order_id')
    order = get_object_or_404(Order, id=order_id, user=request.user)

    items = order.items.select_related("product")
    total = sum(item.price * item.quantity for item in items)

    return render(request, "frontend/payment.html", {
        "order": order,
        "items": items,
        "total": total
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def complete_payment(request):
    if request.method == "POST":
        order_id = request.session.get('checkout_order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)

        payment_method = request.POST.get("payment_method")
        if payment_method in ["cod", "vnpay"]:
            order.status = "paid"
        order.save()

        if 'checkout_order_id' in request.session:
            del request.session['checkout_order_id']

        # Redirect trực tiếp bằng name của URL, không cần namespace
        return redirect('personal-page')

    return redirect('checkout_payment')

# orders/views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from my_app.models_Product import Product
from .models import Order, OrderItem


@require_POST
@login_required
def checkout_from_cart(request):
    data = json.loads(request.body)
    ids = data.get("ids", [])

    if not ids:
        return JsonResponse({"error": "no items"}, status=400)

    cart = request.session.get("cart", {})

    # ❌ Xóa order cart cũ
    Order.objects.filter(user=request.user, status="cart").delete()

    # ✅ Tạo order mới
    order = Order.objects.create(user=request.user, status="cart")

    for pid in ids:
        pid = str(pid)
        if pid in cart:
            product = Product.objects.get(id=pid)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart[pid]["quantity"],  # ✅ LẤY SỐ LƯỢNG
                price=product.discount_price           # ✅ LẤY GIÁ TỪ DB
            )

    # ✅ Lưu order id vào session
    request.session["checkout_order_id"] = order.id

    return JsonResponse({"ok": True})
