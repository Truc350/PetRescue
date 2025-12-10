from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, null=True, blank=True)
    image = models.URLField(max_length=500)

    price = models.IntegerField()                      # giá gốc
    discount_price = models.IntegerField(              # giá sau giảm
        null=True,
        blank=True
    )

    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    size_label = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Tên hiển thị cho nhóm Size (ví dụ 'Huong')"
    )

    def __str__(self):
        return self.name

    def final_price(self):
        """Trả về giá cuối cùng: giá giảm hoặc giá gốc"""
        return self.discount_price if self.discount_price else self.price

    def discount_percent(self):
        """Tính % giảm tự động"""
        if self.discount_price:
            return int((1 - self.discount_price / self.price) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.URLField(max_length=500)

    def __str__(self):
        return f"Image of {self.product.name}"


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size_name = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.size_name}"

from django.db import models
from django.contrib.auth.models import User  # hoặc model User custom nếu bạn có

class ProductReview(models.Model):
    STAR_CHOICES = [(i, f"{i} sao") for i in range(1, 6)]

    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)  # nếu user không login
    rating = models.IntegerField(choices=STAR_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=True)  # dùng nếu muốn duyệt trước khi hiển thị

    class Meta:
        ordering = ["-created_at"]  # hiển thị mới nhất trước

    def __str__(self):
        user_info = self.user.username if self.user else self.email
        return f"{user_info} - {self.product.name} ({self.rating} sao)"
