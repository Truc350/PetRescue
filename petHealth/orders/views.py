from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from datetime import timedelta, datetime
from calendar import monthrange
import json

from .models import Order, OrderItem, ShippingAddress
from my_app.models_Product import Product
from .vnpay import VNPay, verify_vnpay_signature


# ============ CHECKOUT & BUY NOW ============

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    order = Order.objects.create(
        user=request.user,
        status="draft"
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )

    request.session['checkout_order_id'] = order.id
    return redirect("orders:checkout_shipping")


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
        cart_key = str(item["id"])
        quantity = int(item["quantity"])

        if cart_key not in cart:
            continue

        cart_item = cart[cart_key]
        product = Product.objects.get(id=cart_item["product_id"])

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=cart_item["price"]
        )

    request.session["checkout_order_id"] = order.id
    request.session.modified = True
    return JsonResponse({"ok": True})


@login_required
def checkout_shipping(request):
    order_id = request.session.get('checkout_order_id')

    if not order_id:
        return redirect("shopping_cart")

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
    vnp_TxnRef = str(order.id)

    if payment_method == "cod":
        order.status = "pending"
        order.save()

        # ✅ XÓA SẢN PHẨM ĐÃ ĐẶT KHỎI GIỎ HÀNG
        cart = request.session.get("cart", {})
        ordered_product_ids = set(str(item.product.id) for item in order.items.all())

        # Xóa các items đã đặt (bao gồm cả các size khác nhau của cùng sản phẩm)
        cart = {k: v for k, v in cart.items() if k.split('_')[0] not in ordered_product_ids}

        request.session["cart"] = cart
        request.session.pop("checkout_order_id", None)
        request.session.modified = True

        return redirect(reverse("personal-page") + "?tab=orders")

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


# ============ VNPAY CALLBACKS ============

def vnpay_return(request):
    params = request.GET.dict()

    if not verify_vnpay_signature(params, settings.VNPAY_HASH_SECRET):
        messages.error(request, "Dữ liệu thanh toán không hợp lệ")
        return redirect(reverse("personal-page") + "?tab=orders")

    # ✅ XÓA SẢN PHẨM ĐÃ ĐẶT KHỎI GIỎ HÀNG SAU THANH TOÁN VNPAY
    response_code = params.get("vnp_ResponseCode")
    order_id = params.get("vnp_TxnRef")

    if response_code == "00" and order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            cart = request.session.get("cart", {})
            ordered_product_ids = set(str(item.product.id) for item in order.items.all())

            # Xóa các items đã đặt khỏi giỏ hàng
            cart = {k: v for k, v in cart.items() if k.split('_')[0] not in ordered_product_ids}

            request.session["cart"] = cart
            request.session.pop("checkout_order_id", None)
            request.session.modified = True
        except Order.DoesNotExist:
            pass

    messages.success(request, "Đã nhận phản hồi từ VNPAY")
    return redirect(reverse("personal-page") + "?tab=orders")


@csrf_exempt
def vnpay_ipn(request):
    input_data = request.GET.dict()

    order_id = input_data.get("vnp_TxnRef")
    response_code = input_data.get("vnp_ResponseCode")
    transaction_status = input_data.get("vnp_TransactionStatus")
    amount = int(input_data.get("vnp_Amount", 0)) // 100

    order = Order.objects.filter(id=order_id).first()
    if not order:
        return JsonResponse({"RspCode": "01", "Message": "Order not found"})

    if order.status in ["shipping", "delivered"]:
        return JsonResponse({"RspCode": "02", "Message": "Order already confirmed"})

    if int(order.total_price) != amount:
        return JsonResponse({"RspCode": "04", "Message": "Invalid amount"})

    if response_code == "00" and transaction_status == "00":
        order.status = "pending"
        order.save()
        return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})

    order.status = "cancel"
    order.save()
    return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})


# ============ ORDER MANAGEMENT ============

@login_required
def personal_page(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "frontend/personal-page.html", {"orders": user_orders})


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


@login_required
def buy_again(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="delivered"
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


# ============ ADMIN STATISTICS ============

@staff_member_required
def order_statistics_view(request):
    # ✅ PHẢI KHAI BÁO NGAY ĐẦU TIÊN
    selected_month = request.GET.get('month', '')
    selected_year = request.GET.get('year', '')
    view_type = request.GET.get('view', '')

    selected_month_int = int(selected_month) if selected_month else None
    selected_year_int = int(selected_year) if selected_year else None

    # Tự động chọn view_type nếu có filter mà chưa chọn view hoặc đang ở view 'week'
    # 'week' mặc định hiển thị 8 tuần gần đây, sẽ bị trống nếu filter tháng/năm quá xa
    if not view_type or (view_type == 'week' and (selected_month or selected_year)):
        if selected_month or selected_year:
            view_type = 'custom'
        else:
            view_type = 'week'

    # Khởi tạo queryset cơ bản
    base_orders = Order.objects.all()

    # Áp dụng bộ lọc tháng/năm
    if selected_month:
        base_orders = base_orders.filter(created_at__month=int(selected_month))
    if selected_year:
        base_orders = base_orders.filter(created_at__year=int(selected_year))

    # Thống kê tổng quan
    total_orders = base_orders.exclude(status='draft').count()
    draft_orders = base_orders.filter(status='draft').count()
    pending_orders = base_orders.filter(status='pending').count()
    shipping_orders = base_orders.filter(status='shipping').count()
    delivered_orders = base_orders.filter(status='delivered').count()
    cancelled_orders = base_orders.filter(status='cancel').count()

    total_revenue = base_orders.filter(
        status='delivered'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_orders_qs = base_orders.filter(
        created_at__gte=thirty_days_ago
    ).exclude(status='draft')
    recent_orders = recent_orders_qs.count()

    recent_revenue = recent_orders_qs.filter(
        status='delivered'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    avg_order_value = base_orders.filter(
        status='delivered'
    ).aggregate(Avg('total_price'))['total_price__avg'] or 0

    # Thống kê theo thời gian
    orders_by_time = []
    chart_title = ""

    if view_type == 'week':
        chart_title = "8 Tuần Gần Đây"
        for i in range(8):
            week_end = timezone.now() - timedelta(weeks=i)
            week_start = week_end - timedelta(days=6)

            week_orders = base_orders.filter(
                created_at__date__gte=week_start.date(),
                created_at__date__lte=week_end.date()
            )

            count = week_orders.exclude(status='draft').count()
            revenue = week_orders.filter(
                status='delivered'
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0

            orders_by_time.append({
                'label': f'{week_start.strftime("%d/%m")} - {week_end.strftime("%d/%m")}',
                'count': count,
                'revenue': float(revenue)
            })
        orders_by_time.reverse()

    elif view_type == 'month':
        if selected_year:
            target_year = int(selected_year)
            chart_title = f"Theo Tháng Năm {target_year}"
        else:
            target_year = timezone.now().year
            chart_title = f"Theo Tháng Năm {target_year}"

        for month in range(1, 13):
            month_orders = base_orders.filter(
                created_at__year=target_year,
                created_at__month=month
            )

            count = month_orders.exclude(status='draft').count()
            revenue = month_orders.filter(
                status='delivered'
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0

            orders_by_time.append({
                'label': f'Tháng {month}',
                'count': count,
                'revenue': float(revenue)
            })

    elif view_type == 'year':
        chart_title = "Thống Kê Theo Năm"
        years_with_orders = Order.objects.dates('created_at', 'year', order='DESC')

        if years_with_orders.exists():
            for year_date in years_with_orders[:5]:
                year = year_date.year

                year_orders = Order.objects.filter(created_at__year=year)

                if selected_month:
                    year_orders = year_orders.filter(created_at__month=int(selected_month))

                count = year_orders.exclude(status='draft').count()
                revenue = year_orders.filter(
                    status='delivered'
                ).aggregate(Sum('total_price'))['total_price__sum'] or 0

                orders_by_time.append({
                    'label': f'Năm {year}',
                    'count': count,
                    'revenue': float(revenue)
                })
            orders_by_time.reverse()
        else:
            current_year = timezone.now().year
            orders_by_time.append({
                'label': f'Năm {current_year}',
                'count': 0,
                'revenue': 0
            })

    elif view_type == 'custom':
        if selected_month and selected_year:
            chart_title = f"Chi Tiết Tháng {selected_month}/{selected_year}"
            target_year = int(selected_year)
            target_month = int(selected_month)

            _, days_in_month = monthrange(target_year, target_month)

            for day in range(1, days_in_month + 1):
                day_orders = base_orders.filter(
                    created_at__year=target_year,
                    created_at__month=target_month,
                    created_at__day=day
                )

                count = day_orders.exclude(status='draft').count()
                revenue = day_orders.filter(
                    status='delivered'
                ).aggregate(Sum('total_price'))['total_price__sum'] or 0

                orders_by_time.append({
                    'label': f'{day:02d}/{target_month:02d}',
                    'count': count,
                    'revenue': float(revenue)
                })

        elif selected_year and not selected_month:
            chart_title = f"12 Tháng Năm {selected_year}"
            target_year = int(selected_year)

            for month in range(1, 13):
                month_orders = base_orders.filter(
                    created_at__year=target_year,
                    created_at__month=month
                )

                count = month_orders.exclude(status='draft').count()
                revenue = month_orders.filter(
                    status='delivered'
                ).aggregate(Sum('total_price'))['total_price__sum'] or 0

                orders_by_time.append({
                    'label': f'Tháng {month}',
                    'count': count,
                    'revenue': float(revenue)
                })

        elif selected_month and not selected_year:
            # Nếu chỉ chọn tháng, hiển thị tháng đó qua các năm
            chart_title = f"Tháng {selected_month} Qua Các Năm"
            target_month = int(selected_month)

            years_with_orders = Order.objects.dates('created_at', 'year', order='ASC')

            if years_with_orders.exists():
                for year_date in years_with_orders:
                    year = year_date.year

                    year_month_orders = base_orders.filter(
                        created_at__year=year,
                        created_at__month=target_month
                    )

                    count = year_month_orders.exclude(status='draft').count()
                    revenue = year_month_orders.filter(
                        status='delivered'
                    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

                    orders_by_time.append({
                        'label': f'{target_month}/{year}',
                        'count': count,
                        'revenue': float(revenue)
                    })
            else:
                # Fallback nếu chưa có đơn nào
                current_year = timezone.now().year
                orders_by_time.append({
                    'label': f'{target_month}/{current_year}',
                    'count': 0,
                    'revenue': 0
                })

        else:
            # Mặc định của custom (nếu không chọn gì) là 12 tháng năm nay
            current_year = timezone.now().year
            chart_title = f"Năm {current_year}"

            for month in range(1, 13):
                month_orders = base_orders.filter(
                    created_at__year=current_year,
                    created_at__month=month
                )

                count = month_orders.exclude(status='draft').count()
                revenue = month_orders.filter(
                    status='delivered'
                ).aggregate(Sum('total_price'))['total_price__sum'] or 0

                orders_by_time.append({
                    'label': f'Tháng {month}',
                    'count': count,
                    'revenue': float(revenue)
                })

    # Top khách hàng
    top_customers = base_orders.filter(
        status='delivered'
    ).values(
        'user__username', 'user__email', 'user__first_name', 'user__last_name'
    ).annotate(
        total_orders=Count('id'),
        total_spent=Sum('total_price')
    ).order_by('-total_spent')[:10]

    # Top sản phẩm
    top_products_qs = OrderItem.objects.filter(order__in=base_orders, order__status='delivered')

    top_products = top_products_qs.values(
        'product__name', 'product__id'
    ).annotate(
        total_quantity=Sum('quantity'),
        # Tạm thời Sum('price') nếu không muốn dùng F object phức tạp, 
        # nhưng đúng nhất phải là Sum(F('price') * F('quantity'))
        total_revenue=Sum('price')
    ).order_by('-total_quantity')[:10]

    # Lý do hủy
    cancel_reasons = base_orders.filter(
        status='cancel',
        cancel_reason__isnull=False
    ).exclude(cancel_reason='').values('cancel_reason').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Tỷ lệ
    total_processed = base_orders.exclude(status='draft').count()
    completion_rate = (delivered_orders / total_processed * 100) if total_processed > 0 else 0
    cancel_rate = (cancelled_orders / total_processed * 100) if total_processed > 0 else 0

    # Danh sách tháng/năm cho dropdown
    months = [{'value': i} for i in range(1, 13)]

    first_order = Order.objects.order_by('created_at').first()
    if first_order:
        start_year = first_order.created_at.year
    else:
        start_year = timezone.now().year

    current_year = timezone.now().year
    years = list(range(start_year, current_year + 1))
    years.reverse()

    orders_by_time_json = json.dumps(orders_by_time)

    context = {
        'total_orders': total_orders,
        'draft_orders': draft_orders,
        'pending_orders': pending_orders,
        'shipping_orders': shipping_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'recent_revenue': recent_revenue,
        'avg_order_value': avg_order_value,
        'orders_by_time': orders_by_time,
        'orders_by_time_json': orders_by_time_json,
        'chart_title': chart_title,
        'view_type': view_type,
        'top_customers': top_customers,
        'top_products': top_products,
        'cancel_reasons': cancel_reasons,
        'completion_rate': round(completion_rate, 1),
        'cancel_rate': round(cancel_rate, 1),
        'selected_month': selected_month_int,
        'selected_year': selected_year_int,
        'filter_applied': bool(selected_month or selected_year),
        'months': months,
        'years': years,
    }

    return render(request, 'admin/orders_statistics.html', context)


# ============ LEGACY / UNUSED ============

@require_POST
def save_checkout_items(request):
    data = json.loads(request.body)
    ids = data.get("ids", [])
    request.session["checkout_product_ids"] = ids
    request.session.modified = True
    return JsonResponse({"ok": True})


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