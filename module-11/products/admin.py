from django.contrib import admin
from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'is_available']
    search_fields = ['name', 'category__name']
    list_filter = ['category', 'is_available']
    actions = ['mark_out_of_stock']
    
    def mark_out_of_stock(self, request, queryset):
        """Custom action to mark products as out of stock"""
        updated = queryset.update(stock=0, is_available=False)
        self.message_user(request, f'{updated} product(s) marked as out of stock.')
    
    mark_out_of_stock.short_description = 'Mark selected products as out of stock'

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)