from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from my_app.models_Product import Product
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Chờ xác nhận"),  # admin xác nhận
        ("shipping", "Đang giao"),  # admin giao hàng
        ("delivered", "Đã giao"),  # hoàn tất
        ("cancel", "Đã hủy"),  # admin hoặc user hủy
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # ✅ SỬA
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    province = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    note = models.TextField(blank=True)
