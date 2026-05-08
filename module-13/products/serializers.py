from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "product_count", "products"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.context.get("include_products", False):
            self.fields.pop("products")

    def get_product_count(self, obj):
        return getattr(obj, "products_total", obj.products.count())

    def get_products(self, obj):
        serializer_context = {**self.context, "include_products": False}
        return ProductSerializer(
            obj.products.all(),
            many=True,
            context=serializer_context,
        ).data


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "stock",
            "is_available",
            "image",
            "created_at",
            "category",
            "category_id",
        ]
        read_only_fields = ["id", "created_at"]
