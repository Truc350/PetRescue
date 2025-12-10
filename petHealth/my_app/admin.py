from django.contrib import admin
from .models_Product import Category, Product, ProductImage, ProductSize

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

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
