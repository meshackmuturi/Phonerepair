from django.urls import path
from . import views

urlpatterns = [
    path("api/customers/", views.register_customer, name="register_customer"),
]
