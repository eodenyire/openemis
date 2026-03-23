from django.contrib import admin
from .models import PaymentCategory, Payment

@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'payment_type', 'category', 'payment_date')
    list_filter = ('payment_type', 'category', 'payment_date', 'academic_year')
    search_fields = ('title', 'description')