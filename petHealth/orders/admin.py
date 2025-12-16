from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress

print(">>> ORDERS ADMIN LOADED <<<")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0
    can_delete = False
    readonly_fields = (
        "full_name",
        "phone",
        "address",
        "province",
        "ward",
        "note",
    )


@admin.action(description="Xác nhận đơn (→ Đang giao)")
def confirm_order(modeladmin, request, queryset):
    queryset.filter(status="pending").update(status="shipping")


@admin.action(description="Hoàn tất giao hàng (→ Đã giao)")
def complete_order(modeladmin, request, queryset):
    queryset.filter(status="shipping").update(status="delivered")


@admin.action(description="Hủy đơn hàng")
def cancel_order(modeladmin, request, queryset):
    queryset.filter(status__in=["pending", "shipping"]).update(status="cancel")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status_label",
        "total_price",
        "created_at",
    )

    list_filter = ("status",)
    search_fields = ("id", "user__username")
    ordering = ("-created_at",)

    readonly_fields = ("user", "total_price", "created_at")

    inlines = [OrderItemInline, ShippingAddressInline]

    actions = [
        confirm_order,
        complete_order,
        cancel_order,
    ]

    def status_label(self, obj):
        return obj.get_status_display()

    status_label.short_description = "Trạng thái"

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return obj.status not in ["delivered", "cancel"]

    def has_view_permission(self, request, obj=None):
        return True
