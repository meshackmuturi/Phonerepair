from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Customer Model
class Customer(models.Model):
    customer_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            last_customer = Customer.objects.all().order_by('id').last()
            if last_customer:
                last_id = int(last_customer.customer_id.split('-')[1])
                self.customer_id = f'CUST-{str(last_id + 1).zfill(6)}'
            else:
                self.customer_id = 'CUST-000001'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer_id} - {self.full_name}"
    
    class Meta:
        ordering = ['-created_at']

# Repair Job Model
class RepairJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('progress', 'In Progress'),
        ('completed', 'Completed'),
        ('ready', 'Ready for Pickup'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]
    
    job_id = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='jobs')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    device_type = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    
    problem_description = models.TextField()
    technician_notes = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateField()
    completed_at = models.DateTimeField(blank=True, null=True)
    
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        if not self.job_id:
            import time
            timestamp = str(int(time.time()))[-6:]
            self.job_id = f'JOB-{timestamp}'
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.job_id} - {self.customer.full_name}"
    
    class Meta:
        ordering = ['-created_at']

# Payment Model
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-PESA'),
        ('card', 'Card'),
    ]
    
    job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.job.job_id} - KSH {self.amount}"
    
    class Meta:
        ordering = ['-payment_date']

# Notification Model  
class Notification(models.Model):
    TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, null=True, blank=True)
    recipient_phone = models.CharField(max_length=15, blank=True, null=True)
    recipient_email = models.EmailField(blank=True, null=True)
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        recipient = self.recipient_phone or self.recipient_email
        return f"{self.notification_type} to {recipient} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']