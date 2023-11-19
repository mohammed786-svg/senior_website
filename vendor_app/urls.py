from django.urls import path
from . import views
from django.conf.urls import handler404, handler500

app_name = 'vendor_app' #namespace
urlpatterns = [
    #To Login Screen
    path('',views.login_view,name='login'),
    #To Welcome Screen
    path('dashboard/',views.dashboard,name='dashboard'),
    #To Welcome Screen
    path('orders/',views.all_orders,name='orders'),
    #To Welcome Screen
    path('profile/',views.profile,name='profile'),
    #To Welcome Screen
    path('notifications/',views.update_notification,name='notifications'),
    #To Welcome Screen
    path('notifications/<int:service_id>/',views.update_notification,name='update_notification'),
]
