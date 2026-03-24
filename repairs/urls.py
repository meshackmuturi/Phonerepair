from django.urls import path
from . import views

urlpatterns = [
    # Customer endpoints
    path('api/register-customer/', views.register_customer, name='register_customer'),
    path('api/get-customers/', views.get_customers, name='get_customers'),
    
    # Job endpoints
    path('api/create-job/', views.create_repair_job, name='create_job'),
    path('api/get-jobs/', views.get_jobs, name='get_jobs'),
    
    # Notification endpoint
    path('api/send-notification/', views.send_notification, name='send_notification'),
    
    # Payment endpoint
    path('api/process-payment/', views.process_payment, name='process_payment'),
]