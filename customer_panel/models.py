from django.db import models
from django.utils import timezone
# Create your models here.

class CustomerRegister(models.Model):
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_email = models.EmailField(unique=True)
    customer_mobileno = models.CharField(max_length=15)
    customer_password = models.CharField(max_length=128) # Use hashing in production
    customer_profile_pic = models.ImageField(upload_to='customer_profiles/', null=True, blank=True)
    customer_username = models.CharField(max_length=100, null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)


class CustomerSubscription(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]

    customer = models.ForeignKey(CustomerRegister, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=10, choices=PLAN_CHOICES)
    duration_months = models.IntegerField()  # 1 or 3
    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Payment tracking fields (NEW)
    amount_paid = models.IntegerField(default=0, verbose_name="Amount Paid (ps)")
    payment_date = models.DateTimeField(null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_receipt = models.CharField(max_length=50, blank=True, null=True, verbose_name="Custom Receipt ID")

    def __str__(self):
       return f"{self.customer.customer_username} - {self.plan_type} - {self.amount_paid} ps"


