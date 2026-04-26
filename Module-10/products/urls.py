from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    
    # Product URLs
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path("products/<int:pk>/delete/", views.delete_product, name="delete_product"),
    
    # Category URLs
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/<int:pk>/edit/", views.edit_category, name="edit_category"),
    path("categories/<int:pk>/delete/", views.delete_category, name="delete_category"),
    
    # About page
    path("about/", views.about, name="about"),
]