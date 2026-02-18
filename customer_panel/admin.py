from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomerRegister, CustomerSubscription


# This allows you to see and edit customers in the admin panel
admin.site.register(CustomerRegister)


@admin.register(CustomerSubscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'plan_type', 'duration_months', 'amount_paid_display', 'payment_date', 'expiry_date', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['customer__customer_username', 'razorpay_payment_id']
    
    def amount_paid_display(self, obj):
        return f"₹{obj.amount_paid // 100}"  # Shows: ₹499
    amount_paid_display.short_description = 'Amount (stored as paise)'
