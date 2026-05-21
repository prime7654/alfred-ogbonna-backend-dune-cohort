from django import forms
from .models import Order, Product, Category


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories"""
    
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter category name'
        }),
        error_messages={
            'required': 'Category name is required.',
            'max_length': 'Category name cannot exceed 100 characters.'
        }
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter category description (optional)',
            'rows': 4
        })
    )
    
    class Meta:
        model = Category
        fields = ['name', 'description']


class ProductForm(forms.ModelForm):
    """Form for creating and editing products"""
    
    name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter product name'
        }),
        error_messages={
            'required': 'Product name is required.',
            'max_length': 'Product name cannot exceed 200 characters.'
        }
    )
    
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter price',
            'step': '0.01',
            'min': '0'
        }),
        error_messages={
            'required': 'Price is required.',
            'invalid': 'Please enter a valid price.',
            'max_digits': 'Price is too large.',
            'max_decimal_places': 'Price can have up to 2 decimal places.'
        }
    )
    
    stock = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter stock quantity',
            'min': '0'
        }),
        error_messages={
            'required': 'Stock quantity is required.',
            'invalid': 'Please enter a valid stock quantity.'
        }
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        error_messages={
            'required': 'Please select a category.'
        }
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe the product, materials, size, or key details',
            'rows': 4
        })
    )

    is_available = forms.BooleanField(
        required=False,
        initial=True,
        label='Product is available',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'is_available', 'image']
    
    def clean_price(self):
        """Validate that price is not negative"""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price
    
    def clean_stock(self):
        """Validate that stock is not negative"""
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('Stock quantity cannot be negative.')
        return stock


class CheckoutForm(forms.ModelForm):
    """Collect delivery details for a customer order."""

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your delivery address',
            'rows': 4
        })
    )

    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address']


class OrderStatusForm(forms.ModelForm):
    """Allow staff users to update fulfillment state."""

    status = forms.ChoiceField(
        choices=Order.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Order
        fields = ['status']
