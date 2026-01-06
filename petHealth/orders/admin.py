from django.contrib import admin
from django.urls import path, reverse
from .models import Order, OrderItem, ShippingAddress

print(">>> ORDERS ADMIN LOADED <<<")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']


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
    list_display = [
        'id',
        'user',
        'status_label',
        'total_price',
        'short_cancel_reason',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'id']
    ordering = ("-created_at",)

    readonly_fields = ['created_at', 'total_price', 'user', 'cancel_reason', 'cancelled_at']

    inlines = [OrderItemInline, ShippingAddressInline]

    actions = [confirm_order, complete_order, cancel_order]

    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('user', 'status', 'total_price', 'created_at')
        }),
        ('Thông tin hủy đơn', {
            'fields': ('cancel_reason', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )

    def status_label(self, obj):
        return obj.get_status_display()
    status_label.short_description = "Trạng thái"

    def short_cancel_reason(self, obj):
        if obj.status == "cancel" and obj.cancel_reason:
            return obj.cancel_reason[:40]
        return "-"
    short_cancel_reason.short_description = "Lý do huỷ"

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return obj.status not in ["delivered", "cancel"]

    def has_view_permission(self, request, obj=None):
        return True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/',
                 self.admin_site.admin_view(self.statistics_view),
                 name='orders_order_statistics'),
        ]
        return custom_urls + urls

    def statistics_view(self, request):
        from .views import order_statistics_view
        return order_statistics_view(request)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['statistics_url'] = reverse('admin:orders_order_statistics')
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__status']
    search_fields = ['product__name', 'order__id']


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['order', 'full_name', 'phone', 'province']
    search_fields = ['full_name', 'phone', 'address']