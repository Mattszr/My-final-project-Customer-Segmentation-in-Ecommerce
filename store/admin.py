from django.contrib import admin
from .models import Category, Customer, Product, Order 
from .models import CustomerStats

@admin.register(CustomerStats)
class CustomerStatsAdmin(admin.ModelAdmin):
    list_display = ('customer', 'recency', 'frequency', 'monetary', 'view_count', 'cart_count', 'purchase_count', 'most_preferred_category', 'updated_at')
    search_fields = ('customer__email',)


admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)