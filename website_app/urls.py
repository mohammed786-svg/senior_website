from django.urls import path
from . import views
app_name = 'website_app' #namespace
urlpatterns = [
    path('', views.index,name='index'),
    path('inbound_call/', views.inbound,name='inbound'),
    path('enroll/', views.enroll,name='enroll'),
    path('senior_citizen/', views.senior_citizen,name='senior_citizen'),
    path('aboutus/', views.about_us,name='aboutus'),
    path('causes/', views.enroll,name='causes'),
    path('service/', views.enroll,name='service'),
    path('testimonial/', views.enroll,name='testimonial'),
    path('contact/', views.contact,name='contact'),
    path('gallery/', views.gallery,name='gallery'),
    path('blogs/', views.blogs,name='blogs'),
    path('blog_single/', views.blog_single,name='blog_single'),
    path('volunteer/', views.volunteer,name='volunteer'),
    path('register_senior_citizen/', views.register_senior_citizen,name='register_senior_citizen'),
    path('donate/', views.donate,name='donate'),
]