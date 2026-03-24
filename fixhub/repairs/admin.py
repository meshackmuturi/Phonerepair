from django.contrib import admin
from .models import Customer, RepairJob, Payment, Notification

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'full_name', 'phone_number', 'email', 'created_at']
    search_fields = ['customer_id', 'full_name', 'phone_number', 'email']
    list_filter = ['created_at']
    readonly_fields = ['customer_id', 'created_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_id', 'full_name', 'phone_number', 'email', 'address')
        }),
        ('System Information', {
            'fields': ('created_at',)
        }),
    )

@admin.register(RepairJob)
class RepairJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'customer', 'device_info', 'status', 'payment_status', 'estimated_cost', 'created_at']
    search_fields = ['job_id', 'customer__full_name', 'customer__phone_number', 'brand', 'model']
    list_filter = ['status', 'payment_status', 'device_type', 'created_at']
    readonly_fields = ['job_id', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('job_id', 'customer', 'technician', 'status')
        }),
        ('Device Details', {
            'fields': ('device_type', 'brand', 'model', 'serial_number')
        }),
        ('Problem & Repair', {
            'fields': ('problem_description', 'technician_notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'completion_date', 'completed_at')
        }),
        ('Payment', {
            'fields': ('estimated_cost', 'payment_status', 'amount_paid')
        }),
    )
    
    def device_info(self, obj):
        return f"{obj.brand} {obj.model}"
    device_info.short_description = 'Device'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['job', 'amount', 'payment_method', 'payment_date']
    search_fields = ['job__job_id', 'reference_number']
    list_filter = ['payment_method', 'payment_date']
    readonly_fields = ['payment_date']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('job', 'amount', 'payment_method', 'reference_number')
        }),
        ('Additional Details', {
            'fields': ('notes', 'payment_date')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['get_recipient', 'notification_type', 'status', 'sent_at', 'created_at']
    search_fields = ['recipient_phone', 'recipient_email', 'job__job_id']
    list_filter = ['notification_type', 'status', 'sent_at', 'created_at']
    readonly_fields = ['created_at', 'sent_at']
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('job', 'notification_type', 'status')
        }),
        ('Recipient', {
            'fields': ('recipient_phone', 'recipient_email')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status Information', {
            'fields': ('created_at', 'sent_at', 'error_message')
        }),
    )
    
    def get_recipient(self, obj):
        return obj.recipient_phone or obj.recipient_email
    get_recipient.short_description = 'Recipient'