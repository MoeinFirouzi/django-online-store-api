from django.contrib import admin
from market.models import Customer, Product, OrderRow, Order

# Register your models here.
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(OrderRow)
admin.site.register(Order)
