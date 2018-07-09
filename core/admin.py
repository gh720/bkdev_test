from django.contrib import admin
from django.contrib.admin import ModelAdmin

from core.models import Customer, ProductDiscount, Category, Product, CartItem, CustomerDiscount


class DiscountAdmin(ModelAdmin):
    list_display = ['id', 'amount', 'category_str', 'started', 'ended']


class ProductAdmin(ModelAdmin):
    list_display = ['id', 'name', 'price', 'category_str', 'effective_discount']


admin.site.register(Category)
admin.site.register(ProductDiscount, DiscountAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer)
admin.site.register(CustomerDiscount)
admin.site.register(CartItem)
