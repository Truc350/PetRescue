from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404

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

    # NEW: Sản phẩm liên quan do admin tự chọn
    related_products = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="related_to"
    )

    def __str__(self):
        return self.name

    def final_price(self):
        now = timezone.now()
        promo = self.category.promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).first()

        if promo:
            return int(self.price * (100 - promo.discount_percent) / 100)

        return self.price

    def discount_percent(self):
        """Tính % giảm tự động"""
        if self.discount_price:
            return int((1 - self.discount_price / self.price) * 100)
        return 0


    def get_related_products(self, limit=10):
        # 1. Ưu tiên sản phẩm admin gán thủ công
        manual = self.related_products.all()
        if manual.exists():
            return manual[:limit]

        # 2. Fallback: cùng thương hiệu
        same_brand = Product.objects.filter(
            brand=self.brand
        ).exclude(id=self.id)
        if same_brand.exists():
            return same_brand[:limit]

        # 3. Fallback: cùng category
        same_category = Product.objects.filter(
            category=self.category
        ).exclude(id=self.id)
        return same_category[:limit]



    def get_active_promotion(self):
        return self.promotions.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        ).first()

    def get_final_price(self):
        promo = self.get_active_promotion()
        if promo:
            return int(self.price * (100 - promo.discount_percent) / 100)
        return self.discount_price or self.price

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


    # 👇 THÊM
    sentiment = models.CharField(
        max_length=10,
        choices=[("positive", "Positive"), ("negative", "Negative")],
        null=True,
        blank=True
    )
    is_spam = models.BooleanField(default=False)

    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=True)  # dùng nếu muốn duyệt trước khi hiển thị

    class Meta:
        ordering = ["-created_at"]  # hiển thị mới nhất trước

    def __str__(self):
        user_info = self.user.username if self.user else self.email
        return f"{user_info} - {self.product.name} ({self.rating} sao)"

from django.db import models
from django.contrib.auth.models import User

class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="wishlisted_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.name}"


# models.py
from django.db import models
from django.core.exceptions import ValidationError

class Promotion(models.Model):
    name = models.CharField(max_length=255)
    discount_percent = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="promotions"
    )

    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="promotions"
    )

    def __str__(self):
        return self.name
