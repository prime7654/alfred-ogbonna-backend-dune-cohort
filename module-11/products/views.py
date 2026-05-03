from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum, Q
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Product, Category
from .forms import ProductForm, CategoryForm

def home(request):
    return render(request, "products/home.html")

def product_list(request):
    """List all products with optional search filter"""
    products = Product.objects.all()
    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(category__name__icontains=search_query))
    
    context = {
        'products': products,
        'search_query': search_query
    }
    return render(request, "products/product_list.html", context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_detail.html", {"product": product})

def add_product(request):
    """Create a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{form.cleaned_data["name"]}" added successfully!')
            return redirect('shop:product_list')
        else:
            # Pass form with errors to template
            return render(request, 'products/product_form.html', {'form': form, 'action': 'Add'})
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {'form': form, 'action': 'Add'})

def edit_product(request, pk):
    """Edit an existing product"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{form.cleaned_data["name"]}" updated successfully!')
            return redirect('shop:product_detail', pk=product.pk)
        else:
            return render(request, 'products/product_form.html', {
                'form': form,
                'action': 'Edit',
                'product': product
            })
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/product_form.html', {
        'form': form,
        'action': 'Edit',
        'product': product
    })

@require_http_methods(["GET", "POST"])
def delete_product(request, pk):
    """Delete a product with confirmation"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('shop:product_list')
    
    return render(request, 'products/product_confirm_delete.html', {'product': product})

def add_category(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{form.cleaned_data["name"]}" added successfully!')
            return redirect('shop:category_list')
        else:
            return render(request, 'products/category_form.html', {'form': form, 'action': 'Add'})
    else:
        form = CategoryForm()
    
    return render(request, 'products/category_form.html', {'form': form, 'action': 'Add'})

def edit_category(request, pk):
    """Edit an existing category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{form.cleaned_data["name"]}" updated successfully!')
            return redirect('shop:category_list')
        else:
            return render(request, 'products/category_form.html', {
                'form': form,
                'action': 'Edit',
                'category': category
            })
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'products/category_form.html', {
        'form': form,
        'action': 'Edit',
        'category': category
    })

@require_http_methods(["GET", "POST"])
def delete_category(request, pk):
    """Delete a category with confirmation"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('shop:category_list')
    
    return render(request, 'products/category_confirm_delete.html', {'category': category})

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

