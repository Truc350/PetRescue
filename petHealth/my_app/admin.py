from django.contrib import admin
from .models_Product import Category, Product, ProductImage, ProductSize

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    fields = ("size_name", "price")

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
        "size_label",  # nhập tên nhóm Size tại đây
    )

    inlines = [ProductImageInline, ProductSizeInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "url")


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ("product", "size_name", "price")

from .models_Product import ProductReview

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "email", "rating", "approved", "created_at")
    list_filter = ("rating", "approved", "created_at")
    search_fields = ("product__name", "user__username", "email", "comment")
    readonly_fields = ("created_at",)
    actions = ["approve_reviews", "disapprove_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
    approve_reviews.short_description = "Duyệt các đánh giá đã chọn"

    def disapprove_reviews(self, request, queryset):
        queryset.update(approved=False)
    disapprove_reviews.short_description = "Bỏ duyệt các đánh giá đã chọn"