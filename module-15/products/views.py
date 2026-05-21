from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST
from rest_framework import filters, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderItem, Product, Category
from .forms import CategoryForm, CheckoutForm, OrderStatusForm, ProductForm
from .pagination import ProductPagination
from .serializers import ProductSerializer, CategorySerializer


CART_SESSION_KEY = "shopping_cart"


def _get_cart(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def _save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def _get_cart_context(request):
    cart = _get_cart(request)
    product_ids = [int(product_id) for product_id in cart.keys() if str(product_id).isdigit()]
    products = {
        str(product.id): product
        for product in Product.objects.select_related("category").filter(id__in=product_ids)
    }
    cleaned_cart = {}
    items = []
    total = Decimal("0.00")
    item_count = 0

    for product_id, quantity in cart.items():
        product = products.get(str(product_id))
        if product is None:
            continue

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        max_quantity = max(product.stock, 0)
        if quantity <= 0 or max_quantity <= 0 or not product.is_available:
            continue

        quantity = min(quantity, max_quantity)
        line_total = product.price * quantity
        cleaned_cart[str(product.id)] = quantity
        total += line_total
        item_count += quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "line_total": line_total,
                "max_quantity": max_quantity,
            }
        )

    if cleaned_cart != cart:
        _save_cart(request, cleaned_cart)

    return {
        "cart_items": items,
        "cart_total": total,
        "cart_item_count": item_count,
    }


def _staff_required(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return True
    messages.error(request, "Only staff users can manage orders.")
    return False

def home(request):
    available_products_qs = (
        Product.objects.select_related("category")
        .filter(is_available=True, stock__gt=0)
        .order_by("-created_at", "name")
    )
    hero_product = available_products_qs.exclude(image="").filter(image__isnull=False).first()
    featured_products = available_products_qs[:3]
    category_preview = (
        Category.objects.annotate(product_count=Count("products"))
        .filter(product_count__gt=0)
        .order_by("name")[:4]
    )
    context = {
        "hero_product": hero_product or available_products_qs.first(),
        "featured_products": featured_products,
        "category_preview": category_preview,
        "total_products": Product.objects.count(),
        "available_products": Product.objects.filter(is_available=True, stock__gt=0).count(),
        "total_categories": Category.objects.count(),
    }
    return render(request, "products/home.html", context)

def product_list(request):
    """List all products with optional search and category filters."""
    products = Product.objects.select_related('category', 'created_by').order_by('name')
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    selected_category = None

    if category_id:
        selected_category = categories.filter(pk=category_id).first()
        if selected_category:
            products = products.filter(category=selected_category)
    
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(category__name__icontains=search_query))
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    }
    return render(request, "products/product_list.html", context)

def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("category", "created_by"), pk=pk)
    can_manage_product = (
        request.user.is_authenticated
        and request.user.is_staff
        and product.created_by_id == request.user.id
    )
    return render(
        request,
        "products/product_detail.html",
        {"product": product, "can_manage_product": can_manage_product},
    )


def cart_detail(request):
    context = _get_cart_context(request)
    return render(request, "products/cart_detail.html", context)


@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not product.is_available or product.stock <= 0:
        messages.error(request, "This product is currently out of stock.")
        return redirect("shop:product_detail", pk=product.pk)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(quantity, 1)
    cart = _get_cart(request)
    product_key = str(product.pk)
    current_quantity = int(cart.get(product_key, 0))
    new_quantity = min(current_quantity + quantity, product.stock)
    cart[product_key] = new_quantity
    _save_cart(request, cart)

    if new_quantity < current_quantity + quantity:
        messages.warning(request, f'Only {product.stock} "{product.name}" item(s) are available.')
    else:
        messages.success(request, f'"{product.name}" added to your cart.')

    next_url = request.POST.get("next")
    if next_url and not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = None
    return redirect(next_url or "shop:cart_detail")


@require_POST
def update_cart_item(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = _get_cart(request)
    product_key = str(product.pk)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        cart.pop(product_key, None)
        messages.success(request, f'"{product.name}" removed from your cart.')
    elif not product.is_available or product.stock <= 0:
        cart.pop(product_key, None)
        messages.error(request, f'"{product.name}" is no longer available.')
    else:
        cart[product_key] = min(quantity, product.stock)
        if quantity > product.stock:
            messages.warning(request, f'Quantity adjusted to the {product.stock} item(s) in stock.')
        else:
            messages.success(request, "Cart updated.")

    _save_cart(request, cart)
    return redirect("shop:cart_detail")


@require_POST
def remove_cart_item(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = _get_cart(request)
    cart.pop(str(product.pk), None)
    _save_cart(request, cart)
    messages.success(request, f'"{product.name}" removed from your cart.')
    return redirect("shop:cart_detail")


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    original_cart = dict(_get_cart(request))
    cart_context = _get_cart_context(request)
    if not cart_context["cart_items"]:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:cart_detail")

    initial = {
        "full_name": request.user.get_full_name() or request.user.username,
        "email": request.user.email,
    }
    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        cart = original_cart
        with transaction.atomic():
            product_ids = [int(product_id) for product_id in cart.keys() if str(product_id).isdigit()]
            products = {
                str(product.id): product
                for product in Product.objects.select_for_update()
                .select_related("category")
                .filter(id__in=product_ids)
            }
            order_lines = []
            total = Decimal("0.00")

            for product_id, quantity in cart.items():
                product = products.get(str(product_id))
                try:
                    quantity = int(quantity)
                except (TypeError, ValueError):
                    quantity = 0

                if product is None or quantity <= 0:
                    continue

                if not product.is_available or product.stock <= 0:
                    messages.error(request, f'"{product.name}" is no longer available.')
                    return redirect("shop:cart_detail")

                if product.stock < quantity:
                    messages.error(
                        request,
                        f'Only {product.stock} "{product.name}" item(s) are available.',
                    )
                    return redirect("shop:cart_detail")

                line_total = product.price * quantity
                total += line_total
                order_lines.append((product, quantity, line_total))

            if not order_lines:
                messages.error(request, "Your cart is empty.")
                return redirect("shop:cart_detail")

            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.save()

            for product, quantity, line_total in order_lines:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=quantity,
                    line_total=line_total,
                )
                product.stock -= quantity
                if product.stock == 0:
                    product.is_available = False
                product.save(update_fields=["stock", "is_available"])

        _save_cart(request, {})
        messages.success(request, f"Order #{order.pk} placed successfully.")
        return redirect("shop:order_detail", pk=order.pk)

    return render(
        request,
        "products/checkout.html",
        {
            "form": form,
            **cart_context,
        },
    )


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related("items"),
        pk=pk,
    )
    if order.user_id != request.user.id and not request.user.is_staff:
        messages.error(request, "You cannot view that order.")
        return redirect("accounts:my_account")

    return render(request, "products/order_detail.html", {"order": order})


@login_required
def staff_order_list(request):
    if not _staff_required(request):
        return redirect("shop:home")

    status = request.GET.get("status", "").strip()
    orders = Order.objects.select_related("user").prefetch_related("items")
    if status:
        orders = orders.filter(status=status)

    return render(
        request,
        "products/staff_order_list.html",
        {
            "orders": orders,
            "status_choices": Order.STATUS_CHOICES,
            "selected_status": status,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def staff_order_detail(request, pk):
    if not _staff_required(request):
        return redirect("shop:home")

    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related("items"),
        pk=pk,
    )
    form = OrderStatusForm(request.POST or None, instance=order)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Order #{order.pk} status updated.")
        return redirect("shop:staff_order_detail", pk=order.pk)

    return render(
        request,
        "products/staff_order_detail.html",
        {
            "order": order,
            "form": form,
        },
    )

@login_required
def add_product(request):
    """Create a new product"""
    if not request.user.is_staff:
        messages.error(request, 'Only staff users can add products.')
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
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
        form = ProductForm(request.POST, request.FILES, instance=product)
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
