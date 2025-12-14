from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, ShippingAddress

@login_required
def checkout_shipping(request):
    order, created = Order.objects.get_or_create(
        user=request.user,
        status="cart"
    )

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

        return redirect("payments:checkout")

    return render(request, "frontend/delivery-infor.html", {
        "order": order,
        "items": order.items.all(),
        "saved_addresses": []
    })

from django.shortcuts import get_object_or_404
from my_app.models_Product import Product
from .models import Order, OrderItem

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Xóa cart cũ nếu có (optional)
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
