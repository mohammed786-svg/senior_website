from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.db import connection, DatabaseError
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout
from django.http import HttpResponseServerError,JsonResponse
from colorama import Fore, Style
from django.utils import timezone
from datetime import datetime
import pytz
import base64
import os
import uuid
import mimetypes
import time
import threading
import json
from geopy.geocoders import Nominatim

#Add all views here.
# Create your views here.
def index(request):
    current_url = request.get_full_path()
    get_location_hierarchy("India")
    return render(request,"index.html",{'current_url': current_url})

def inbound(request):
    return HttpResponse("This is in bound Form")

def enroll(request):
    return HttpResponse("This is Enroll Now")

def senior_citizen(request):
    return HttpResponse("This is senior_citizen")

def about_us(request):
    current_url = request.get_full_path()
    return render(request,"about.html",{'current_url': current_url})

def gallery(request):
    current_url = request.get_full_path()
    return render(request,"gallery.html",{'current_url': current_url})

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        emailid = request.POST.get('emailid')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        print(subject)
        print(emailid)
        try:
            send_mail(
                subject,
                message,
                emailid,  # Sender's email address
                ["shahidmaniyar888@gmail.com"],  # Recipient's email address
            )
        except Exception as e:
            print(e)
        '''
        try:
            with connection.cursor() as cursor:
                    usertbl_query = "INSERT INTO senior.semails_tbl "
                    cursor.execute(usertbl_query)
                connection.commit()

                print("Email Sent Successfully")
                return redirect('website_app:contact')
                return redirect(reverse('all_sub_categories', kwargs={'catid': catid,'catname':catname}))
        except Exception as e:
            print(f"Error loading data: {e}")'''
            
    current_url = request.get_full_path()
    return render(request,"contact.html",{'current_url': current_url})

def blogs(request):
    current_url = request.get_full_path()
    return render(request,"blogs.html",{'current_url': current_url})

def blog_single(request):
    current_url = request.get_full_path()
    return render(request,"blogs_single.html",{'current_url': current_url})

def volunteer(request):
    current_url = request.get_full_path()
    return render(request,"volunteer.html",{'current_url': current_url})

def register_senior_citizen(request):
    current_url = request.get_full_path()
    if request.method == "POST":
        jdict = json.loads(request.body)
        uname = jdict['fullname']
        primary_mobno = jdict['primaryno']
        whatsapp_no = jdict['whatsappno']
        age = jdict['age']
        gender = jdict['gender']
        address = jdict['fulladdress']
        country = jdict['country']
        state = jdict['state']
        district = jdict['district']
        taluk = jdict['taluk']
        pincode = jdict['pincode']
        city = jdict['city']
        land_mark = jdict['landmark']
        date_of_birth = jdict['dateofbirth']
        queries = jdict['questions']
    # if request.method == "POST":
    #     uname = request.POST.get('fullname')
    #     primary_mobno = request.POST.get('primaryno')
    #     whatsapp_no = request.POST.get('whatsappno')
    #     age = request.POST.get('age')
    #     gender = request.POST.get('gender')
    #     address = request.POST.get('fulladdress')
    #     country = request.POST.get('country')
    #     state = request.POST.get('state')
    #     district = request.POST.get('district')
    #     taluk = request.POST.get('taluk')
    #     pincode = request.POST.get('pincode')
    #     city = request.POST.get('city')  
    #     land_mark = request.POST.get('landmark')
    #     date_of_birth = request.POST.get('dateofbirth')
    #     queries = request.POST.get('questions')
    #     if not queries:
    #         queries = 'No queries'
    #     errors = []
    #     if not uname:
    #         errors.append('Full Name is required.')
    #     if errors:
    #         # If there are validation errors, render the form with error messages
    #         return render(request, 'admin_pages/add_senior_citizen.html', {'errors': errors})
        
        try:
            with connection.cursor() as cursor:
                # Insert a new senior citizen
                usertbl_query = "INSERT INTO senior.susertbl (usrname, mobno, whatsappno, address) VALUES ('"+str(uname)+"', '"+str(primary_mobno)+"', '"+str(whatsapp_no)+"', '"+str(address)+"') RETURNING usrid"
                cursor.execute(usertbl_query)
                usrid = cursor.fetchone()[0]  # Retrieve the returned usrid
                insert_query = (
                    "INSERT INTO senior.senior_citizens (uname, primary_mobno, whatsapp_no, age, gender, address, "
                    "country, state, district, taluk, pincode, city, land_mark, date_of_birth, usrid,queries) "
                    "VALUES ('"+str(uname)+"', '"+str(primary_mobno)+"', '"+str(whatsapp_no)+"', '"+str(age)+"', '"+str(gender)+"'"
                    ", '"+str(address)+"', '"+str(country)+"', '"+str(state)+"', '"+str(district)+"', '"+str(taluk)+"', '"+str(pincode)+"',"
                    "'"+str(city)+"', '"+str(land_mark)+"', '"+str(date_of_birth)+"', '"+str(usrid)+"','"+str(queries)+"')"
                )
                print(f"Create New user details::{insert_query}")
                cursor.execute(insert_query)
                connection.commit()

                print("Senior Citizen Added Successfully.")
                response_data = {'message': 'Senior citizen created successfully'}
                return JsonResponse(response_data)
                #return redirect('website_app:index')
        except Exception as e:
            print(f"Error loading data: {e}")
            # Handle GET request or other scenarios
            return JsonResponse({'message': 'Invalid request'})
    return render(request,"register_senior_citizens.html",{'current_url': current_url})

def donate(request):
    current_url = request.get_full_path()
    return render(request,"donate.html",{'current_url': current_url})

def get_location_hierarchy(country_name):
    geolocator = Nominatim(user_agent="geoapiExercises")
    
    # Fetch country details
    country_data = geolocator.geocode(country_name, exactly_one=True)
    
    if country_data:
        # Get the country code
        country_code = country_data.raw.get('display_name', '').split(', ')[-1]
        
        # Fetch states
        states = geolocator.geocode(country_code, exactly_one=True, featuretype="state")
        print("States in", country_name)
        print(states)

        # Fetch districts
        districts = geolocator.geocode(country_code, exactly_one=True, featuretype="district")
        print("Districts in", country_name)
        print(districts)

        # Fetch cities
        cities = geolocator.geocode(country_code, exactly_one=True, featuretype="city")
        print("Cities in", country_name)
        print(cities)

        # Fetch taluks (if available)
        taluks = geolocator.geocode(country_code, exactly_one=True, featuretype="taluks")
        print("Taluks in", country_name)
        print(taluks)


