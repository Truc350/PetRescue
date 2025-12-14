from django.contrib import admin
from .models_Product import (
    Category,
    Product,
    ProductImage,
    ProductSize,
    ProductReview,
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
    list_display = ("name", "brand", "price", "discount_price", "final_price")
    search_fields = ("name",)
    list_filter = ("brand", "category")

    prepopulated_fields = {"slug": ("name",)}

    fields = (
        "name",
        "slug",
        "brand",
        "image",
        "price",
        "discount_price",
        "description",
        "category",
        "size_label",  # Nhóm size
    )

    inlines = [ProductImageInline, ProductSizeInline]


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

from django.contrib import admin
from .models_Product import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")
    ordering = ("-created_at",)