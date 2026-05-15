from django.contrib import admin
from .models import Product, Category

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
