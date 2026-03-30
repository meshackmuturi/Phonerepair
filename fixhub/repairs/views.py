from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Customer, RepairJob, Payment, Notification
import json
from datetime import datetime

# API: Register Customer
@csrf_exempt
@require_http_methods(["POST"])
def register_customer(request):
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        if not data.get('fullName') or not data.get('phoneNumber'):
            return JsonResponse({
                'success': False,
                'error': 'Full name and phone number are required'
            }, status=400)
        
        # Create customer
        customer = Customer.objects.create(
            full_name=data['fullName'],
            phone_number=data['phoneNumber'],
            email=data.get('email', ''),
            address=data.get('address', '')
        )
        
        return JsonResponse({
            'success': True,
            'customer_id': customer.customer_id,
            'message': 'Customer registered successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# API: Get All Customers
@require_http_methods(["GET"])
def get_customers(request):
    try:
        customers = Customer.objects.all()
        
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

# API: Create Repair Job
@csrf_exempt
@require_http_methods(["POST"])
def create_repair_job(request):
    try:
        data = json.loads(request.body)
        
        # Get customer
        customer = get_object_or_404(Customer, id=data['customer_id'])
        
        # Create job
        job = RepairJob.objects.create(
            customer=customer,
            device_type=data['deviceType'],
            brand=data['brand'],
            model=data['model'],
            serial_number=data.get('serial', ''),
            problem_description=data['problem'],
            technician_notes=data.get('notes', ''),
            completion_date=data['completionDate'],
            estimated_cost=data['cost'],
            payment_status=data['paymentStatus'],
            amount_paid=data.get('amountPaid', 0)
        )
        
        return JsonResponse({
            'success': True,
            'job_id': job.job_id,
            'message': 'Repair job created successfully'
        })
        
    except Customer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Customer not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# API: Get All Jobs
@require_http_methods(["GET"])
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

# API: Get Single Job
@require_http_methods(["GET"])
def get_job(request, job_id):
    try:
        job = get_object_or_404(RepairJob, job_id=job_id)
        
        job_data = {
            'job_id': job.job_id,
            'customer_name': job.customer.full_name,
            'customer_phone': job.customer.phone_number,
            'customer_email': job.customer.email or '',
            'device_type': job.device_type,
            'brand': job.brand,
            'model': job.model,
            'serial_number': job.serial_number or '',
            'problem': job.problem_description,
            'notes': job.technician_notes or '',
            'status': job.status,
            'estimated_cost': str(job.estimated_cost),
            'payment_status': job.payment_status,
            'amount_paid': str(job.amount_paid),
            'completion_date': str(job.completion_date),
            'created_at': job.created_at.strftime('%Y-%m-%d %H:%M')
        }
        
        return JsonResponse({
            'success': True,
            'job': job_data
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
        }, status=500)

# API: Update Job Status
@csrf_exempt
@require_http_methods(["POST"])
def update_job_status(request, job_id):
    try:
        data = json.loads(request.body)
        job = get_object_or_404(RepairJob, job_id=job_id)
        
        job.status = data['status']
        job.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Job status updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# API: Send Notification
@csrf_exempt
@require_http_methods(["POST"])
def send_notification(request):
    try:
        data = json.loads(request.body)
        
        # Create notification record
        notification = Notification.objects.create(
            recipient_phone=data.get('phone', ''),
            recipient_email=data.get('email', ''),
            notification_type=data['type'],
            subject=data.get('subject', ''),
            message=data['message'],
            status='sent'  # Will be 'pending' when SMS/Email integration added
        )
        
        # TODO: Add actual SMS/Email sending here
        # For now, just save to database
        notification.sent_at = timezone.now()
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification sent successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# API: Dashboard Stats
@require_http_methods(["GET"])
def dashboard_stats(request):
    try:
        total_jobs = RepairJob.objects.count()
        pending_jobs = RepairJob.objects.filter(status='pending').count()
        progress_jobs = RepairJob.objects.filter(status='progress').count()
        completed_jobs = RepairJob.objects.filter(status='completed').count()
        
        # Calculate revenue
        from django.db.models import Sum
        total_revenue = RepairJob.objects.aggregate(
            total=Sum('estimated_cost')
        )['total'] or 0
        
        paid_revenue = RepairJob.objects.aggregate(
            paid=Sum('amount_paid')
        )['paid'] or 0
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_jobs': total_jobs,
                'pending_jobs': pending_jobs,
                'progress_jobs': progress_jobs,
                'completed_jobs': completed_jobs,
                'total_revenue': str(total_revenue),
                'paid_revenue': str(paid_revenue)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# API: Recent Activity
@require_http_methods(["GET"])
def recent_activity(request):
    try:
        # Get recent jobs
        recent_jobs = RepairJob.objects.all()[:10]
        
        activities = []
        for job in recent_jobs:
            activities.append({
                'type': 'job_created',
                'job_id': job.job_id,
                'customer': job.customer.full_name,
                'status': job.status,
                'timestamp': job.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        
        @csrf_exempt
def register_customer(request):
    if request.method == "POST":
        data = json.loads(request.body)
        customer = Customer.objects.create(
            full_name=data["full_name"],
            phone_number=data["phone_number"],
            email=data.get("email", "")
        )
        return JsonResponse({"id": customer.id, "status": "success"})
