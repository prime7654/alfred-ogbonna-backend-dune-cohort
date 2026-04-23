from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from .models import Product, Category

def home(request):
    return render(request, "products/home.html")

def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {"products": products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_detail.html", {"product": product})

def category_list(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    total_products = Product.objects.count()
    return render(request, "products/category_list.html", {
        "categories": categories,
        "total_products": total_products
    })

def about(request):
    return render(request, "products/about.html")

def custom_404(request, exception=None):
    return render(request, "products/404.html", status=404)

