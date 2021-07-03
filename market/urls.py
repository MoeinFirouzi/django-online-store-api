from django.urls import path

from . import views

urlpatterns = [
    # products urls
    path('product/insert/', views.product_insert, name='product_insert'),
    path('product/list/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_information, name='product_information'),
    path('product/<int:product_id>/edit_inventory/', views.edit_inventory, name='edit_inventory'),
    path('shopping/cart/', views.customer_cart, name='cart'),
    path('shopping/cart/add_items/', views.add_items, name='add_items'),
    path('shopping/cart/remove_items/', views.remove_items, name='remove_items'),
    path('shopping/submit/', views.submit, name='submit')
    # TODO: insert other url paths
    # path(...
    # path(...
    # path(...
]
