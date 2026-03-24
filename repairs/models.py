from django.db import models
from django.utils import timezone
import random
import string

class Customer(models.Model):
    customer_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            last_customer = Customer.objects.all().order_by('id').last()
            if last_customer:
                last_number = int(last_customer.customer_id.split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.customer_id = f'CUST-{str(new_number).zfill(6)}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_id} - {self.full_name}"


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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='repair_jobs')
    
    # Device Information
    device_type = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, blank=True)
    
    # Problem Details
    problem_description = models.TextField()
    
    # Job Details
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional
    technician_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.job_id:
            timestamp = str(int(timezone.now().timestamp()))
            self.job_id = f'JOB-{timestamp}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.job_id} - {self.customer.full_name}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-PESA'),
        ('card', 'Card'),
    ]

    job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.job_id} - KSH {self.amount}"


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    recipient_phone = models.CharField(max_length=20, blank=True)
    recipient_email = models.EmailField(blank=True)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} to {self.recipient_phone or self.recipient_email}"