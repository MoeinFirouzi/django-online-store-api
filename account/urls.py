from django.urls import path

from . import views

urlpatterns = [
    path('customer/register/', views.register_customer, name='register'),
    path('customer/list/', views.customer_list, name='search'),
    path('customer/<int:customer_id>/', views.customer_information, name='customer_information'),
    path('customer/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customer/login/', views.login_customer, name='login_customer'),
    path('customer/logout/', views.logout_customer, name='logout_customer'),
    path('customer/profile/', views.customer_profile, name='customer_profile')
]
