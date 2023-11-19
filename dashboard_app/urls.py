from django.urls import path
from . import views
from django.conf.urls import handler404, handler500

app_name = 'dashboard_app' #nameSpace 

urlpatterns = [
    #To Login Screen
    path('',views.login_view,name='login'),
    #To Welcome Screen
    path('dashboard/',views.dashboard,name='dashboard'),
    #To Update Admin or My Profile
    path('profile/',views.profile_view,name='profile'),
    #To Search Senior Citizen
    path('search_citizen/',views.search_senior_citizen,name='search_citizen'),
    #To View all senior citizen
    path('senior_citizens/',views.all_senior_citizens,name='senior_citizens'),
    #To Add New Senior citizen 
    path('senior_citizens/add_senior_citizen/',views.add_senior_citizen,name='add_senior_citizen'),
    #To Update existing data
    path('senior_citizens/update_senior_citizen/<int:usrid>/',views.add_senior_citizen,name='update_senior_citizen'),
    #To delete Senior Citizen
    path('delete_senior_citizen/<int:usrid>/',views.delete_senior_citizen,name='delete_senior_citizen'),
    #To Load all Volunteers
    path('volunteers/',views.all_volunteers,name='volunteers'),
    #To Add New Volunteer 
    path('volunteers/add_volunteer/',views.add_new_volunteer,name='add_volunteer'),
    #To Update Volunteer existing data
    path('volunteers/update_volunteer/<int:usrid>/',views.add_new_volunteer,name='update_volunteer'),
    #To delete volunteer
    path('delete_volunteer/<int:usrid>/',views.delete_volunteer,name='delete_volunteer'),
    #To Load all Vendors
    path('vendors/',views.all_vendors,name='vendors'),
    #To Add New Volunteer 
    path('vendors/add_vendor/',views.add_new_vendor,name='add_vendor'),
    #To Update existing data
    path('vendors/update_vendor/<int:usrid>/',views.add_new_vendor,name='update_vendor'),
    #To delete vendor
    path('delete_vendor/<int:usrid>/',views.delete_vendor,name='delete_vendor'),
    #To All Services
    path('services/',views.all_service_requests,name='services'),
    #To Create a Service Request 
    path('services/create_service/',views.create_new_service_request,name='create_service'),
    
    
    
    #To Logout
    path('logout/', views.logout_view, name='logout'),
]

# Custom error handlers
handler404 = views.custom_404_view 
handler500 = views.custom_500_view 