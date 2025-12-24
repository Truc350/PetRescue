from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, ShippingAddress


@login_required
def checkout_shipping(request):
    order_id = request.session.get('checkout_order_id')

    if not order_id:
        # Nếu không có order trong session → redirect về buy_now hoặc giỏ hàng
        return redirect("shopping_cart")  # thay cart_view bằng view giỏ hàng của bạn

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

    order = Order.objects.create(
        user=request.user,
        status="draft"
    )
    # order = Order.objects.create(
    #     user=request.user,
    #     status="pending"
    # )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )

    request.session['checkout_order_id'] = order.id
    return redirect("orders:checkout_shipping")


import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden


@require_POST
def save_checkout_items(request):
    data = json.loads(request.body)
    ids = data.get("ids", [])

    request.session["checkout_product_ids"] = ids
    request.session.modified = True

    return JsonResponse({"ok": True})


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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse  # ✅ THÊM DÒNG NÀY
from .models import Order


@login_required
def complete_payment(request):
    if request.method == "POST":
        order_id = request.session.get("checkout_order_id")

        if not order_id:
            return redirect(reverse("personal-page") + "?tab=orders")

        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != "pending":
            return redirect(reverse("personal-page") + "?tab=orders")

        payment_method = request.POST.get("payment_method")
        if payment_method not in ["cod", "vnpay"]:
            return redirect("orders:checkout_payment")

        order.payment_method = payment_method
        order.calculate_total()
        order.save()

        request.session.pop("checkout_order_id", None)

        return redirect(reverse("personal-page") + "?tab=orders")

    return redirect("orders:checkout_payment")


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

    order = Order.objects.create(
        user=request.user,
        status="draft"
    )

    for pid in ids:
        pid = str(pid)
        if pid in cart:
            product = Product.objects.get(id=pid)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart[pid]["quantity"],  # ✅ LẤY SỐ LƯỢNG
                price=product.discount_price  # ✅ LẤY GIÁ TỪ DB
            )

            # ✅ XÓA SẢN PHẨM KHỎI CART
            del cart[pid]

        # ✅ LƯU LẠI CART
    request.session["cart"] = cart
    request.session.modified = True

    # ✅ Lưu order id vào session
    request.session["checkout_order_id"] = order.id

    return JsonResponse({"ok": True})


# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Order

from django.contrib.auth.decorators import login_required


@login_required
def personal_page(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "frontend/personal-page.html", {"orders": user_orders})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def order_detail_api(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        return HttpResponseForbidden("Bạn không có quyền xem đơn này")

    items = []
    for item in order.items.all():
        items.append({
            "name": item.product.name,
            "image": item.product.image if item.product.image else "",
            "quantity": item.quantity,
            "price": int(item.price),
        })

    shipping = None
    if hasattr(order, "shippingaddress"):
        shipping = {
            "full_name": order.shippingaddress.full_name,
            "phone": order.shippingaddress.phone,
            "address": order.shippingaddress.address,
            "province": order.shippingaddress.province,
            "ward": order.shippingaddress.ward,
            "note": order.shippingaddress.note,
        }

    return JsonResponse({
        "id": order.id,
        "status": order.status,
        "created_at": order.created_at.strftime("%d/%m/%Y %H:%M"),
        "total_price": order.total_price,
        "items": items,
        "shipping": shipping,
    })
