from django.contrib import admin
from .models import Category, Order, OrderItem, Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'is_available', 'created_by']
    search_fields = ['name', 'category__name', 'created_by__username']
    list_filter = ['category', 'is_available', 'created_by']
    actions = ['mark_out_of_stock']

    def save_model(self, request, obj, form, change):
        # When a product is created from the admin, keep ownership consistent
        # with the API by storing the logged-in admin user.
        if not change and obj.created_by_id is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def mark_out_of_stock(self, request, queryset):
        """Custom action to mark products as out of stock"""
        updated = queryset.update(stock=0, is_available=False)
        self.message_user(request, f'{updated} product(s) marked as out of stock.')
    
    mark_out_of_stock.short_description = 'Mark selected products as out of stock'

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "unit_price", "quantity", "line_total"]
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "status", "total_amount", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["id", "full_name", "email", "user__username"]
    inlines = [OrderItemInline]
    readonly_fields = ["user", "full_name", "email", "phone", "address", "total_amount", "created_at", "updated_at"]


admin.site.register(Order, OrderAdmin)
