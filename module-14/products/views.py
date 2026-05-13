from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework import filters, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from .pagination import ProductPagination
from .serializers import ProductSerializer, CategorySerializer

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

@login_required
def add_product(request):
    """Create a new product"""
    if not request.user.is_staff:
        messages.error(request, 'Only staff users can add products.')
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f'Product "{form.cleaned_data["name"]}" added successfully!')
            return redirect('shop:product_list')
        else:
            # Pass form with errors to template
            return render(request, 'products/product_form.html', {'form': form, 'action': 'Add'})
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {'form': form, 'action': 'Add'})

@login_required
def edit_product(request, pk):
    """Edit an existing product"""
    if not request.user.is_staff:
        messages.error(request, 'Only staff users can edit products.')
        return redirect('shop:product_list')

    product = get_object_or_404(Product, pk=pk)

    if product.created_by_id != request.user.id:
        messages.error(request, 'Only the product creator can edit this product.')
        return redirect('shop:product_detail', pk=product.pk)
    
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

@login_required
@require_http_methods(["GET", "POST"])
def delete_product(request, pk):
    """Delete a product with confirmation"""
    if not request.user.is_staff:
        messages.error(request, 'Only staff users can delete products.')
        return redirect('shop:product_list')

    product = get_object_or_404(Product, pk=pk)

    if product.created_by_id != request.user.id:
        messages.error(request, 'Only the product creator can delete this product.')
        return redirect('shop:product_detail', pk=product.pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('shop:product_list')
    
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def add_category(request):
    """Create a new category"""
    if not request.user.is_staff:
        messages.error(request, 'Only staff users can add categories.')
        return redirect('shop:category_list')

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

@login_required
def edit_category(request, pk):
    """Edit an existing category"""
    if not request.user.is_staff:
        messages.error(request, 'Only staff users can edit categories.')
        return redirect('shop:category_list')

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
@login_required
def delete_category(request, pk):
    """Delete a category with confirmation"""
    if not request.user.is_staff:
        messages.error(request, 'Only staff users can delete categories.')
        return redirect('shop:category_list')

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


class IsProductCreatorOrReadOnly(permissions.BasePermission):
    """Allow public reads, but protect writes with token auth and ownership."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # POST/PUT/DELETE must come from a logged-in user with a valid token.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only the same user saved in Product.created_by can update or delete.
        return obj.created_by_id == request.user.id


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related("category", "created_by").order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsProductCreatorOrReadOnly]
    pagination_class = ProductPagination
    # Query examples:
    # ?category=1&is_available=true&search=shoe&ordering=-price
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_available"]
    search_fields = ["name"]
    ordering_fields = ["price"]
    http_method_names = ["get", "post", "head", "options"]

    def perform_create(self, serializer):
        # Product ownership always comes from the authenticated token user.
        serializer.save(created_by=self.request.user)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related("category", "created_by")
    serializer_class = ProductSerializer
    permission_classes = [IsProductCreatorOrReadOnly]
    http_method_names = ["get", "put", "delete", "head", "options"]


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        return (
            Category.objects.annotate(products_total=Count("products"))
            .prefetch_related("products__category", "products__created_by")
            .order_by("id")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["include_products"] = True
        return context
