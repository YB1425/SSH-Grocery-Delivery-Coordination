from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cart/<int:cart_id>/', views.shared_cart_view, name='shared_cart'),
    path('cart/<int:cart_id>/add/', views.add_item, name='add_item'),
    path('cart/<int:cart_id>/remove/<int:item_id>/', views.remove_item, name='remove_item'),
    path('cart/<int:cart_id>/modify/<int:item_id>/', views.modify_item, name='modify_item'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('create_cart/', views.create_cart, name='create_cart'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('history/', views.user_history, name='user_history'),
] 
