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
from django.conf import settings
from .models import Order
from .vnpay import VNPay

@login_required
def complete_payment(request):
    if request.method != "POST":
        return redirect("orders:checkout_payment")

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
    order.status = "pending"
    order.save()
    vnp_TxnRef = str(order.id)  # ✅ CHUẨN

    # COD → hoàn thành ngay
    if payment_method == "cod":
        order.status = "paid"
        order.save()

        request.session.pop("checkout_order_id", None)
        return redirect(reverse("personal-page") + "?tab=orders")

    # VNPAY → redirect sang cổng thanh toán
    vnpay = VNPay(
        settings.VNPAY_TMN_CODE,
        settings.VNPAY_HASH_SECRET,
        settings.VNPAY_PAYMENT_URL,
        settings.VNPAY_RETURN_URL,
    )

    payment_url = vnpay.create_payment_url(
        request=request,
        order_id=vnp_TxnRef,
        amount=int(order.total_price),
        order_desc=f"Thanh toan don hang #{order.id}",
    )

    return redirect(payment_url)

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
    items = data.get("items", [])

    if not items:
        return JsonResponse({"error": "no items"}, status=400)

    cart = request.session.get("cart", {})

    order = Order.objects.create(
        user=request.user,
        status="draft"
    )

    for item in items:
        pid = str(item["id"])
        quantity = int(item["quantity"])

        if pid in cart:
            product = Product.objects.get(id=pid)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=cart[pid]["price"]
            )

            del cart[pid]
        request.session["cart"] = cart

    # KHÔNG xóa cart ở đây (tùy bạn)
        request.session["checkout_order_id"] = order.id
        request.session.modified = True
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

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def buy_again(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="delivered"   # ❗ chỉ cho mua lại đơn đã giao
    )

    cart = request.session.get("cart", {})

    for item in order.items.select_related("product"):
        product = item.product
        pid = str(product.id)

        if pid in cart:
            cart[pid]["quantity"] += item.quantity
        else:
            cart[pid] = {
                "name": product.name,
                "price": product.final_price,
                "image": str(product.image),
                "slug": product.slug,
                "quantity": item.quantity
            }

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({
        "success": True,
        "redirect": "/shoppingcart"
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json

@login_required
@require_POST
def cancel_order_api(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "pending":
        return JsonResponse({"success": False, "message": "Không thể huỷ đơn này"})

    data = json.loads(request.body)
    reason = data.get("reason", "").strip()

    if not reason:
        return JsonResponse({"success": False, "message": "Thiếu lý do huỷ"})

    order.status = "cancel"
    order.cancel_reason = reason
    order.cancelled_at = timezone.now()
    order.save()

    return JsonResponse({"success": True})

from django.contrib import messages

def vnpay_return(request):
    params = request.GET.dict()

    if not verify_vnpay_signature(params, settings.VNPAY_HASH_SECRET):
        messages.error(request, "Dữ liệu thanh toán không hợp lệ")
        return redirect(reverse("personal-page") + "?tab=orders")

    messages.success(request, "Đã nhận phản hồi từ VNPAY")
    return redirect(reverse("personal-page") + "?tab=orders")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Order
from .vnpay import verify_vnpay_signature


@csrf_exempt
def vnpay_ipn(request):
    input_data = request.GET.dict()

    order_id = input_data.get("vnp_TxnRef")
    response_code = input_data.get("vnp_ResponseCode")
    transaction_status = input_data.get("vnp_TransactionStatus")
    amount = int(input_data.get("vnp_Amount", 0)) // 100  # ✅ FIX

    order = Order.objects.filter(id=order_id).first()
    if not order:
        return JsonResponse({"RspCode": "01", "Message": "Order not found"})

    # chống gọi lại
    if order.status in ["shipping", "delivered"]:
        return JsonResponse({"RspCode": "02", "Message": "Order already confirmed"})

    # check tiền
    if int(order.total_price) != amount:
        return JsonResponse({"RspCode": "04", "Message": "Invalid amount"})

    # thành công
    if response_code == "00" and transaction_status == "00":
        order.status = "shipping"
        order.save()
        return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})

    # thất bại / huỷ
    order.status = "cancel"
    order.save()
    return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})
