from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("shipping/", views.checkout_shipping, name="checkout_shipping"),
    path("save-checkout-items/", views.save_checkout_items, name="save_checkout_items"),
    path("delivery/", views.delivery_info, name="delivery_info"),

]
