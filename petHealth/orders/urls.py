from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("shipping/", views.checkout_shipping, name="checkout_shipping"),
    path("save-checkout-items/", views.save_checkout_items, name="save_checkout_items"),
    path("delivery/", views.delivery_info, name="delivery_info"),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/complete/', views.complete_payment, name='complete_payment'),
    path("checkout/from-cart/", views.checkout_from_cart, name="checkout_from_cart"),
    path("checkout/shipping/", views.checkout_shipping, name="checkout_shipping"),
    path("orders/<int:order_id>/", views.order_detail_api, name="order_detail_api"),
    path("buy-again/<int:order_id>/", views.buy_again, name="buy_again"),
    path("cancel/<int:order_id>/", views.cancel_order_api, name="cancel_order_api"),
    path("vnpay/return/", views.vnpay_return, name="vnpay-return"),
    path("vnpay/ipn/", views.vnpay_ipn, name="vnpay-ipn"),
]
