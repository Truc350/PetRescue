from django.contrib import admin
from django import forms
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models_Product import (
    Category,
    Product,
    ProductImage,
    ProductSize,
    ProductReview,
    Wishlist,
    Promotion,
)

# ======================
# INLINE MODELS
# ======================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    fields = ("size_name", "price")

# ======================
# PRODUCT ADMIN
# ======================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price", "discount_price", "final_price", "import_date" , "expiry_date", "is_new_product", "is_expired")
    search_fields = ("name",)
    list_filter = ("brand", "category", "expiry_date")
    date_hierarchy = 'expiry_date'
    prepopulated_fields = {"slug": ("name",)}

    fields = (
        "name",
        "slug",
        "brand",
        "image",
        "import_date",
        "expiry_date",
        "price",
        "discount_price",
        "description",
        "category",
        "size_label",  # Nhóm size
    )

    inlines = [ProductImageInline, ProductSizeInline]

    # ===== HIỂN THỊ CỘT "SẢN PHẨM MỚI" =====
    def is_new_product(self, obj):
        return obj.is_new_product()

    is_new_product.boolean = True
    is_new_product.short_description = "SP Mới?"

    # ===== PROMOTION THEO CATEGORY =====
    def get_promotion(self, obj):
        now = timezone.now()

        # 1️⃣ promotion theo product
        promo = obj.promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        ).order_by("-discount_percent").first()

        if promo:
            return f"-{promo.discount_percent}% (SP)"

        # 2️⃣ promotion theo category
        if obj.category:
            promo = obj.category.promotions.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now,
            ).order_by("-discount_percent").first()

            if promo:
                return f"-{promo.discount_percent}% (DM)"

        return "-"

    get_promotion.short_description = "Khuyến mãi"

    def final_price(self, obj):
        now = timezone.now()

        # 1️⃣ theo product
        promo = obj.promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        ).order_by("-discount_percent").first()

        if promo:
            return int(obj.price * (100 - promo.discount_percent) / 100)

        # 2️⃣ theo category
        if obj.category:
            promo = obj.category.promotions.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now,
            ).order_by("-discount_percent").first()

            if promo:
                return int(obj.price * (100 - promo.discount_percent) / 100)

        # 3️⃣ fallback logic cũ
        if obj.discount_price and obj.discount_price > 0:
            return obj.discount_price

        return obj.price

    final_price.short_description = "Giá sau KM"

# ======================
# CATEGORY ADMIN
# ======================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

# ======================
# PRODUCT IMAGE ADMIN
# ======================

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "url")

# ======================
# PRODUCT SIZE ADMIN
# ======================

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ("product", "size_name", "price")

# ======================
# PRODUCT REVIEW ADMIN
# ======================

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "email", "rating", "approved", "created_at")
    list_filter = ("rating", "approved", "created_at")
    search_fields = ("product__name", "user__username", "email", "comment")
    readonly_fields = ("created_at",)

    actions = ["approve_reviews", "disapprove_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
    approve_reviews.short_description = "Duyệt đánh giá đã chọn"

    def disapprove_reviews(self, request, queryset):
        queryset.update(approved=False)
    disapprove_reviews.short_description = "Bỏ duyệt đánh giá đã chọn"

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")
    ordering = ("-created_at",)


class PromotionAdminForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        categories = cleaned_data.get("categories")
        products = cleaned_data.get("products")

        if categories and products:
            raise ValidationError(
                "Chỉ chọn Danh mục HOẶC Sản phẩm, không được chọn cả hai."
            )

        if not categories and not products:
            raise ValidationError(
                "Phải chọn ít nhất 1 Danh mục hoặc 1 Sản phẩm."
            )

        return cleaned_data

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    form = PromotionAdminForm

    list_display = ("name", "discount_percent", "start_date",
                    "end_date", "is_active")
    filter_horizontal = ("categories", "products")
    list_filter = ("is_active", "start_date",
                   "end_date",)
    search_fields = ("name",)

    class Media:
        js = ("my_app/js/promotion_admin.js",)
