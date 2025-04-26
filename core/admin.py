from django.contrib import admin
from .models import User, Vendor, Product, Order, OrderItem

# Register User model (using the custom User model)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    search_fields = ('username', 'email')

admin.site.register(User, UserAdmin)

# Register Vendor model
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name',)

admin.site.register(Vendor, VendorAdmin)

# Register Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'stock')
    list_filter = ('vendor',)
    search_fields = ('name', 'vendor__name')

admin.site.register(Product, ProductAdmin)

# Register Order model
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'status', 'created_at', 'total')
    list_filter = ('status', 'customer')
    search_fields = ('customer__username',)

admin.site.register(Order, OrderAdmin)

# Register OrderItem model
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')

admin.site.register(OrderItem, OrderItemAdmin)
