from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),

    # API URLs
    path("api/products/", views.ProductListCreateAPIView.as_view(), name="api_product_list"),
    path("api/products/<int:pk>/", views.ProductDetailAPIView.as_view(), name="api_product_detail"),
    path("api/categories/", views.CategoryListAPIView.as_view(), name="api_category_list"),
    
    # Product URLs
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path("products/<int:pk>/delete/", views.delete_product, name="delete_product"),

    # Cart, checkout, and order URLs
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:pk>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:pk>/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("staff/orders/", views.staff_order_list, name="staff_order_list"),
    path("staff/orders/<int:pk>/", views.staff_order_detail, name="staff_order_detail"),
    
    # Category URLs
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/<int:pk>/edit/", views.edit_category, name="edit_category"),
    path("categories/<int:pk>/delete/", views.delete_category, name="delete_category"),
    
    # About page
    path("about/", views.about, name="about"),
]
