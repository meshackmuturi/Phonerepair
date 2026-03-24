from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Customer, RepairJob, Payment, Notification
import json

# ================================
# CUSTOMER ENDPOINTS
# ================================

@csrf_exempt
def register_customer(request):
    """
    Register a new customer
    POST /api/register-customer/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            customer = Customer.objects.create(
                full_name=data['fullName'],
                phone_number=data['phoneNumber'],
                email=data.get('email', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Customer registered successfully',
                'customer_id': customer.customer_id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_customers(request):
    """
    Get all customers
    GET /api/get-customers/
    """
    try:
        customers = Customer.objects.all().order_by('-created_at')
        customers_data = []
        
        for customer in customers:
            customers_data.append({
                'id': customer.id,
                'customer_id': customer.customer_id,
                'full_name': customer.full_name,
                'phone_number': customer.phone_number,
                'email': customer.email or '',
                'created_at': customer.created_at.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({
            'success': True,
            'customers': customers_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ================================
# JOB ENDPOINTS
# ================================

@csrf_exempt
def create_repair_job(request):
    """
    Create a new repair job
    POST /api/create-job/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            print("Received data:", data)
            
            customer = Customer.objects.get(id=data['customer_id'])
            
            job = RepairJob.objects.create(
                customer=customer,
                device_type=data['deviceType'],
                brand=data['brand'],
                model=data['model'],
                serial_number=data.get('serial', ''),
                problem_description=data['problem'],
                estimated_cost=data['cost'],
                completion_date=data['dueDate'],
                status='pending',
                payment_status=data.get('paymentStatus', 'pending'),
                amount_paid=data.get('amountPaid', 0),
                technician_notes=data.get('notes', '')
            )
            
            print("Job created:", job.job_id)
            
            return JsonResponse({
                'success': True,
                'message': 'Job created successfully',
                'job_id': job.job_id
            })
            
        except Customer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Customer not found'
            }, status=404)
        except KeyError as e:
            return JsonResponse({
                'success': False,
                'error': f'Missing required field: {str(e)}'
            }, status=400)
        except Exception as e:
            print("Error creating job:", str(e))
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_jobs(request):
    """
    Get all repair jobs
    GET /api/get-jobs/
    """
    try:
        jobs = RepairJob.objects.all().order_by('-created_at')
        jobs_data = []
        
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'job_id': job.job_id,
                'customer_id': job.customer.id,
                'customer_name': job.customer.full_name,
                'customer_phone': job.customer.phone_number,
                'customer_email': job.customer.email or '',
                'device_type': job.device_type,
                'brand': job.brand,
                'model': job.model,
                'serial_number': job.serial_number,
                'problem': job.problem_description,
                'status': job.status,
                'cost': str(job.estimated_cost),
                'payment_status': job.payment_status,
                'amount_paid': str(job.amount_paid),
                'due_date': job.completion_date.strftime('%Y-%m-%d') if job.completion_date else '',
                'notes': job.technician_notes,
                'created_at': job.created_at.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({
            'success': True,
            'jobs': jobs_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ================================
# NOTIFICATION ENDPOINTS
# ================================

@csrf_exempt
def send_notification(request):
    """
    Send SMS or Email notification
    POST /api/send-notification/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            notification_type = data['type']
            message = data['message']
            
            notification = Notification.objects.create(
                recipient_phone=data.get('phone', ''),
                recipient_email=data.get('email', ''),
                notification_type=notification_type,
                subject=data.get('subject', ''),
                message=message,
                status='pending'
            )
            
            if notification_type == 'sms' and data.get('phone'):
                try:
                    from .sms_utils import send_sms
                    sms_result = send_sms(data['phone'], message)
                    
                    if sms_result['success']:
                        notification.status = 'sent'
                        notification.sent_at = timezone.now()
                        notification.save()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'SMS sent successfully'
                        })
                    else:
                        notification.status = 'failed'
                        notification.error_message = sms_result['message']
                        notification.save()
                        
                        return JsonResponse({
                            'success': False,
                            'error': 'Failed to send SMS: ' + sms_result['message']
                        }, status=400)
                except ImportError:
                    notification.status = 'sent'
                    notification.sent_at = timezone.now()
                    notification.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'SMS logged (sending not configured)'
                    })
            
            elif notification_type == 'email' and data.get('email'):
                try:
                    from .email_utils import send_email_notification
                    email_result = send_email_notification(
                        to_email=data['email'],
                        subject=data.get('subject', 'Notification from FixHub'),
                        message=message
                    )
                    
                    if email_result['success']:
                        notification.status = 'sent'
                        notification.sent_at = timezone.now()
                        notification.save()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Email sent successfully'
                        })
                    else:
                        notification.status = 'failed'
                        notification.error_message = email_result['message']
                        notification.save()
                        
                        return JsonResponse({
                            'success': False,
                            'error': 'Failed to send email: ' + email_result['message']
                        }, status=400)
                except ImportError:
                    notification.status = 'sent'
                    notification.sent_at = timezone.now()
                    notification.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Email logged (sending not configured)'
                    })
            
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Notification logged'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# ================================
# PAYMENT ENDPOINTS
# ================================

@csrf_exempt
def process_payment(request):
    """
    Process payment for a job
    POST /api/process-payment/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            job = RepairJob.objects.get(id=data['job_id'])
            
            payment = Payment.objects.create(
                job=job,
                amount=data['amount'],
                payment_method=data['method'],
                reference_number=data.get('mpesa_code', ''),
                notes=data.get('notes', '')
            )
            
            job.payment_status = 'paid'
            job.amount_paid = data['amount']
            job.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Payment processed successfully',
                'payment_id': payment.id
            })
            
        except RepairJob.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Job not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)