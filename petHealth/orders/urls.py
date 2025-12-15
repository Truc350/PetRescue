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

]
