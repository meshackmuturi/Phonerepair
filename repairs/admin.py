from django.contrib import admin
from .models import Customer, RepairJob, Payment, Notification

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'full_name', 'phone_number', 'email', 'created_at']
    search_fields = ['customer_id', 'full_name', 'phone_number']
    readonly_fields = ['customer_id', 'created_at']

@admin.register(RepairJob)
class RepairJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'customer', 'brand', 'model', 'status', 'estimated_cost']
    search_fields = ['job_id', 'customer__full_name']
    list_filter = ['status', 'payment_status']
    readonly_fields = ['job_id', 'created_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['job', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_type', 'status', 'sent_at']
    list_filter = ['notification_type', 'status']