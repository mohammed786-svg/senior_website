from django.shortcuts import render,redirect
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

# Create your views here.

def handle_database_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Database error: {e}")
            return HttpResponseServerError("A database error occurred. Please try again later.")
    return wrapper

@never_cache
def login_view(request):
    print("Login View is being called")
    alert_message = None
    if request.method == "POST":
        username = request.POST.get('uname')
        password = request.POST.get('passwrd')
        query = "select adminid,username,password from senior.sadmintbl where username='"+str(username)+"' and password='"+str(password)+"'"
        print("query::"+str(query))
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                user_data = cursor.fetchone()

            if user_data and user_data[2]:
                # User is authorized
                print(user_data[0])
                request.session['user_id'] = user_data[0]
                request.session['username'] = user_data[1]
                request.session['password'] = user_data[2]
                request.session['is_logged_in'] = True
                # Setting the session to expire after one day (86400 seconds)
                request.session.set_expiry(86400)
                
                return redirect('dashboard_app:dashboard')
            else:
                # If the login is unsuccessful, store the form data in the context
                context = {
                'username': username,
                'password': password,
                'error_message': 'Invalid credentials',  # You can customize this error message
                }
                return render(request, 'admin_pages/login.html', context)
            
            
        except Exception as e:
            # Handle database-related exceptions here
            alert_message = f"An error occurred: {str(e)}"
            
    return render(request,"admin_pages/login.html",{'error_message': alert_message})

@never_cache
def logout_view(request):
    print('trying to logout')
    logout(request)
    request.session['is_logged_in'] = False
    return redirect('dashboard_app:login')

def profile_view(request):
    return render(request,'admin_pages/profile.html')

def dashboard(request):
    
    loggedIN = isLoggedIn(request)
    if loggedIN == False:
        return redirect('dashboard_app:login')
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    return render(request, 'admin_pages/dashboard.html', {'current_url': current_url})

def search_senior_citizen(request):
    error_code = "No Senior Citizen Found with this mobile number"
    if request.method == "POST":
        search_no = request.POST.get("search_no")
        query = "SELECT usrid FROM senior.senior_citizens WHERE primary_mobno = '"+str(search_no)+"'"
        row = execute_raw_query_fetch_one(query)
        if not row == 500:
            data = {
                'usrid': row[0],
            }
            response_data = {
                'exists':True,
                'data':data
                             }
            return redirect('dashboard_app:update_senior_citizen',usrid=data.get('usrid'))
        else:
            response_data = {
                'exists':False,
                'error_code':error_code
                }
        return redirect('dashboard_app:add_senior_citizen')
    return redirect('dashboard_app:dashboard')
    

def all_senior_citizens(request):
    error_msg = "No Senior Citizen Data Found"
    query = "SELECT usrid, uname, primary_mobno, whatsapp_no, age, gender, address, seniorid FROM senior.senior_citizens order by uname desc"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500 and not query_result == 400:
        for row in query_result:
            data.append({
                'usrid': row[0],
                'uname': row[1],
                'primary_mobno': row[2],
                'whatsapp_no': row[3],
                'age': row[4],
                'gender': row[5],
                'address': row[6],
                'seniorid': row[7]
            })
    else:
        error_msg = 'Something Went Wrong. [Please Try after sometime ]'
        
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return render(request,'admin_pages/all_senior_citizen.html',context)

def all_vendors(request):
    error_msg = "No Vendors Data Found"
    query = "select vendorid,vendor_name,business_name,manager_or_owner_name,id_proof,shop_type,do_you_home_delivery,area_locality,coverage_km,time_of_opertn,working_days,home_delivery_min_cost,other_notes,mobno,whatsappno,svendortbl.address,age,gender,pincode,land_mark,date_of_birth,svendortbl.usrid from senior.svendortbl,senior.susertbl where susertbl.usrid=svendortbl.usrid order by vendorid desc"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500 and not query_result == 400:
        for row in query_result:
            canHomeDelivery = row[6]
            print(f'canHomeDelievry::{canHomeDelivery}')
            if canHomeDelivery == 1:
                canHomeDelivery = 'Yes'
            else:
                canHomeDelivery = 'No'
            data.append({
                'vendorid': row[0],
                'vendor_name': row[1],
                'business_name': row[2],
                'manager_or_owner_name': row[3],
                'id_proof': row[4],
                'shop_type': row[5],
                'do_you_home_delivery': canHomeDelivery,
                'area_locality': row[7],
                'coverage_km': row[8],
                'time_of_opertn': row[9],
                'working_days': row[10],
                'home_delivery_min_cost': row[11],
                'other_notes': row[12],
                'mobno': row[13],
                'whatsapp_no': row[14],
                'address': row[15],
                'age': row[16],
                'gender': row[17],
                'pincode': row[18],
                'land_mark': row[19],
                'date_of_birth': row[20],
                'usrid': row[21]
            })
    else:
        error_msg = 'Something Went Wrong. [Please Try after sometime ]'
        
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return render(request,'admin_pages/all_vendors.html',context)


def all_volunteers(request):
    error_msg = "No Volunteers Data Found"
    query = "select volunteer_id,volunteer_name,work_hrs,work_timing,work_days,skill_name,can_drive,mobno,whatsappno,address,age,gender,svolunteerstbl.usrid from senior.svolunteerstbl,senior.susertbl where susertbl.usrid=svolunteerstbl.usrid order by volunteer_id desc"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500 and not query_result == 400:
        for row in query_result:
            data.append({
                'volunteer_id': row[0],
                'volunteer_name': row[1],
                'work_hrs': row[2],
                'work_timing': row[3],
                'work_days': row[4],
                'skill_name': row[5],
                'can_drive': row[6],
                'whatsappno': row[7],
                'primaryno': row[8],
                'address': row[9],
                'age': row[10],
                'gender': row[11],
                'usrid': row[12],
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return render(request,'admin_pages/all_volunteers.html',context)



def add_senior_citizen(request,usrid=None):
    if request.method == "POST":
        uname = request.POST.get('fullname')
        primary_mobno = request.POST.get('primaryno')
        whatsapp_no = request.POST.get('whatsappno')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('fulladdress')
        country = request.POST.get('country')
        state = request.POST.get('state')
        district = request.POST.get('district')
        taluk = request.POST.get('taluk')
        pincode = request.POST.get('pincode')
        city = request.POST.get('city')  
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        queries = request.POST.get('questions')
        if not queries:
            queries = 'No queries'
        errors = []
        if not uname:
            errors.append('Full Name is required.')
        if errors:
            # If there are validation errors, render the form with error messages
            return render(request, 'admin_pages/add_senior_citizen.html', {'errors': errors})
        
        try:
            with connection.cursor() as cursor:
                if usrid:
                    # Update an existing senior citizen
                    update_query = (
                        "UPDATE senior.senior_citizens SET uname='"+str(uname)+"', primary_mobno='"+str(primary_mobno)+"', whatsapp_no='"+str(whatsapp_no)+"', age='"+str(age)+"', gender='"+str(gender)+"', "
                        "address='"+str(address)+"', country='"+str(country)+"', state='"+str(state)+"', district='"+str(district)+"', taluk='"+str(taluk)+"', pincode='"+str(pincode)+"', city='"+str(city)+"', land_mark='"+str(land_mark)+"', "
                        "date_of_birth='"+str(date_of_birth)+"',queries='"+str(queries)+"' WHERE usrid='"+str(usrid)+"'"
                    )
                    print(f"update user details::{update_query}")
                    cursor.execute(update_query)
                else:
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

                print("Senior Citizen Added/Updated Successfully.")
                return redirect('dashboard_app:senior_citizens')
        except Exception as e:
            print(f"Error loading data: {e}")

    
    # If usrid is provided, retrieve the data for the selected senior citizen
    data = {}
    print(usrid)
    if usrid:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT uname, primary_mobno, whatsapp_no, age, gender, address, country, "
                               "state, district, taluk, pincode, city, land_mark, date_of_birth,queries "
                               "FROM senior.senior_citizens WHERE usrid = '"+str(usrid)+"'")
                row = cursor.fetchone()
                print(f'fetching the single user data::{row}')
                if row:
                    data = {
                        'usrid': usrid,
                        'fullname': row[0],
                        'primaryno': row[1],
                        'whatsappno': row[2],
                        'age': row[3],
                        'gender': row[4],
                        'fulladdress': row[5],
                        'country': row[6],
                        'state': row[7],
                        'district': row[8],
                        'taluk': row[9],
                        'pincode': row[10],
                        'city': row[11],
                        'landmark': row[12],
                        'dateofbirth': row[13],
                        'questions': row[14],
                    }
        except Exception as e:
            print(f"Error loading data: {e}") 
        
    return render(request,'admin_pages/add_senior_citizen.html',{'data': data})


def add_new_volunteer(request,usrid=None):
    if request.method == "POST":
        volunteer_name = request.POST.get('fullname')
        primary_mobno = request.POST.get('primaryno')
        whatsapp_no = request.POST.get('whatsappno')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('fulladdress')
        pincode = request.POST.get('pincode')
        city_id = request.POST.get('city')  
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        workhours = request.POST.get('how_much_time_weekly')
        operate = request.POST.get('operate')
        skillname = request.POST.get('skillname')
        otherskill = request.POST.get('otherskill')
        workdays = request.POST.getlist('workdays')
        worktiming = request.POST.get('worktiming')
        othernotes = request.POST.get('othernotes')
        about_me = request.POST.get('about_me')
        candrive = request.POST.get('candrive')
        
        multiple_workdays = ','.join(workdays)
        if skillname == 'Other' and otherskill:
            select_skill_name = otherskill
        else:
            select_skill_name = skillname
        
        if not othernotes:
            othernotes = 'NA'
        if not about_me:
            about_me = 'NA'
        
        errors = []
        if not volunteer_name:
            errors.append('Full Name is required.')
        if errors:
            # If there are validation errors, render the form with error messages
            return render(request, 'admin_pages/add_volunteer.html', {'errors': errors})
        
        try:
            with connection.cursor() as cursor:
                if usrid:
                    # Update an existing volunteer
                    update_query = (
                        "UPDATE senior.svolunteerstbl"
                        " SET "
                            "volunteer_name='"+str(volunteer_name)+"',"
                            "work_hrs='"+str(workhours)+"',"
                            "work_timing='"+str(worktiming)+"',"
                            "work_days='"+str(multiple_workdays)+"',"
                            "operate_any='"+str(operate)+"',"
                            "anything_else_about_me='"+str(about_me)+"',"
                            "skill_name='"+str(select_skill_name)+"',"
                            "other_notes='"+str(othernotes)+"',"
                            "can_drive='"+str(candrive)+"',"
                            "date_of_birth='"+str(date_of_birth)+"',"
                            "pincode='"+str(pincode)+"'"
                        "WHERE"
                            " usrid='"+str(usrid)+"'"
                    )
                    print(f"update volunteer details::{update_query}")
                    cursor.execute(update_query)
                else:
                    # Insert a new volunteer
                    usertbl_query = "INSERT INTO senior.susertbl (usrname, mobno, whatsappno, address,age,gender) VALUES ('"+str(volunteer_name)+"', '"+str(primary_mobno)+"', '"+str(whatsapp_no)+"', '"+str(address)+"','"+str(age)+"','"+str(gender)+"') RETURNING usrid"
                    print(usertbl_query)
                    cursor.execute(usertbl_query)
                    usrid = cursor.fetchone()[0]  # Retrieve the returned usrid

                    insert_query = (
                        "insert into senior.svolunteerstbl(volunteer_name,work_hrs,work_timing,work_days,operate_any,anything_else_about_me,skill_name,other_notes,can_drive,usrid,date_of_birth,pincode,city_id,landmark) "
                        "values ('"+str(volunteer_name)+"','"+str(workhours)+"','"+str(worktiming)+"','"+str(multiple_workdays)+"','"+str(operate)+"','"+str(about_me)+"','"+str(select_skill_name)+"','"+str(othernotes)+"','"+str(candrive)+"','"+str(usrid)+"','"+str(date_of_birth)+"','"+str(pincode)+"','"+str(city_id)+"','"+str(land_mark)+"')"
                    )
                    print(f"Create New Volunteers details::{insert_query}")
                    cursor.execute(insert_query)
                connection.commit()

                print("Volunteer Added/Updated Successfully.")
                return redirect('dashboard_app:volunteers')
        except Exception as e:
            print(f"Error loading data: {e}")

    query_country = "select countryid,country_name from senior.countrytbl"
    row_country = execute_raw_query(query_country)
    country_data = []
    if not row_country == 500:
        for row in row_country:
            country_data.append({
                'country_id': row[0],
                'country_name': row[1],                
            })
    query_state = "select state_id,state_name from senior.statetbl"
    row_state = execute_raw_query(query_state)
    state_data = []
    if not row_state == 500:
        for row in row_state:
            state_data.append({
                'state_id': row[0],
                'state_name': row[1],                
            })
    query_city = "select city_id,city_name from senior.citytbl"
    row_city = execute_raw_query(query_city)
    city_data = []
    if not row_city == 500:
        for row in row_city:
            city_data.append({
                'city_id': row[0],
                'city_name': row[1],                
            })
            
    query_district = "select district_id,district_name from senior.districttbl"
    row_district = execute_raw_query(query_district)
    district_data = []
    if not row_district == 500:
        for row in row_district:
            district_data.append({
                'district_id': row[0],
                'district_name': row[1],                
            })
    query_taluk = "select taluk_id,taluk_name from senior.taluktbl"
    row_taluk = execute_raw_query(query_taluk)
    taluk_data = []
    if not row_taluk == 500:
        for row in row_taluk:
            taluk_data.append({
                'taluk_id': row[0],
                'taluk_name': row[1],                
            })
    
    # If usrid is provided, retrieve the data for the selected volunteer
    context = {}
    data = {}
    print(usrid)
    if usrid:
        error_msg = "No Volunteer Data Found"
        query = "select volunteer_id,volunteer_name,work_hrs,work_timing,work_days,skill_name,can_drive,mobno,whatsappno,address,age,gender,city_name,taluk_name,district_name,country_name,pincode,landmark,date_of_birth,state_name,anything_else_about_me,operate_any,other_notes from senior.svolunteerstbl,senior.susertbl,senior.citytbl,senior.statetbl,senior.countrytbl,senior.districttbl,senior.taluktbl where svolunteerstbl.city_id=citytbl.city_id and susertbl.usrid=svolunteerstbl.usrid and citytbl.state_id = statetbl.state_id and statetbl.country_id = countrytbl.countryid and citytbl.city_id = districttbl.city_id and districttbl.district_id = taluktbl.district_id  and svolunteerstbl.usrid='"+str(usrid)+"'"
        row = execute_raw_query_fetch_one(query)
        data = []    
        print(f'row[0]------>{row[0]}')
        if not row == 500:
                 if row:
                    data = {
                        'usrid': usrid,
                        'volunteer_id': row[0],
                        'volunteer_name': row[1],
                        'work_hrs': row[2],
                        'work_timing': row[3],
                        'work_days': row[4],
                        'skill_name': row[5],
                        'can_drive': row[6],
                        'mobno': row[7],
                        'whatsappno': row[8],
                        'address': row[9],
                        'age': row[10],
                        'gender': row[11],
                        'city_name': row[12],
                        'taluk_name': row[13],
                        'district_name': row[14],
                        'country_name': row[15],
                        'pincode': row[16],
                        'landmark': row[17],
                        'dateofbirth': row[18],
                        'state_name': row[19],
                        'about_me': row[20],
                        'operate_any': row[21],
                        'othernotes': row[22],
                        
                    }
                    
       
        else:
            error_msg = 'Something Went Wrong. [Please Try after sometime ]'
            
       
   
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    context = {
        'data': data,
        'all_days':all_days,
        'country_data': country_data,
        'state_data': state_data,
        'city_data': city_data,
        'district_data': district_data,
        'taluk_data': taluk_data,
        }    
    return render(request,'admin_pages/add_volunteer.html',context)


def add_new_vendor(request,usrid=None):
    if request.method == "POST":
        vendorname = request.POST.get('vendorname')
        businessname = request.POST.get('businessname')
        ownername = request.POST.get('ownername')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        aadharno = request.POST.get('aadharno')
        primaryno = request.POST.get('primaryno')
        whatsappno = request.POST.get('whatsappno')
        shop_type = request.POST.get('shop')
        othershop = request.POST.get('othershop')
        canhomedelivery = request.POST.get('canhomedelivery')
        homedeliverycost = request.POST.get('mindeliverycharges')
        worktiming = request.POST.get('worktiming')
        workdays = request.POST.getlist('workdays')
        address = request.POST.get('fulladdress')
        coverage_km = request.POST.get('minareakm')
        area_locality = request.POST.get('locality')
        pincode = request.POST.get('pincode')
        city_id = request.POST.get('city')  
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        notes = request.POST.get('notes')
        username = request.POST.get('username')
        password = request.POST.get('password')
        service_name = request.POST.get('service_name')
        
        multiple_workdays = ','.join(workdays)
        
        
        if not notes:
            notes = 'No queries'
        if not othershop:
            othershop = 'NA'
        
        try:
            with connection.cursor() as cursor:
                if usrid:
                    # Update an existing senior citizen
                    update_query = (
                        " UPDATE senior.svendortbl SET "
                            "vendor_name = '"+str(vendorname)+"',"
                            "business_name = '"+str(businessname)+"',"
                            "manager_or_owner_name = '"+str(ownername)+"',"
                            "id_proof = '"+str(aadharno)+"',"
                            "shop_type = '"+str(shop_type)+"',"
                            "do_you_home_delivery = '"+str(canhomedelivery)+"',"
                            "area_locality = '"+str(area_locality)+"',"
                            "coverage_km = '"+str(coverage_km)+"',"
                            "address = '"+str(address)+"',"
                            "cityid = '"+str(city_id)+"',"
                            "time_of_opertn = '"+str(worktiming)+"',"
                            "working_days = '"+str(multiple_workdays)+"',"
                            "home_delivery_min_cost = '"+str(homedeliverycost)+"',"
                            "other_notes = '"+str(notes)+"',"
                            "date_of_birth='"+str(date_of_birth)+"',"
                            "pincode='"+str(pincode)+"',"
                            "land_mark='"+str(land_mark)+"',"
                            "other_shop_type_name='"+str(othershop)+"',"
                            "service_type='"+str(service_name)+"'"
                            " where usrid='"+str(usrid)+"'"
                        
                    )
                    print(f"update user details::{update_query}")
                    cursor.execute(update_query)
                    update_login_query = "update senior.sadmintbl set password='"+str(password)+"', username='"+str(username)+"' where usrid='"+str(usrid)+"'";
                    cursor.execute(update_login_query)
                else:
                    # Insert a new vendor
                    usertbl_query = "INSERT INTO senior.susertbl (usrname, mobno, whatsappno, address, age, gender) VALUES ('"+str(vendorname)+"', '"+str(primaryno)+"', '"+str(whatsappno)+"', '"+str(address)+"', '"+str(age)+"', '"+str(gender)+"') RETURNING usrid"
                                    
                    cursor.execute(usertbl_query)
                    usrid = cursor.fetchone()[0]  # Retrieve the returned usrid

                    insert_query = (
                       " INSERT INTO senior.svendortbl ("
                            "vendor_name,"
                            "business_name,"
                            "manager_or_owner_name,"
                            "id_proof,"
                            "shop_type,"
                            "do_you_home_delivery,"
                            "area_locality,"
                            "coverage_km,"
                            "address,"
                            "cityid,"
                            "time_of_opertn,"
                            "working_days,"
                            "home_delivery_min_cost,"
                            "other_notes,"
                            "date_of_birth,"
                            "pincode,"
                            "land_mark,"
                            "other_shop_type_name,"
                            "usrid,"
                            "service_type"
                        ")"
                       " VALUES ("
                            "'"+str(vendorname)+"',"
                            "'"+str(businessname)+"',"
                            "'"+str(ownername)+"',"
                            "'"+str(aadharno)+"',"
                            "'"+str(shop_type)+"',"
                            "'"+str(canhomedelivery)+"',"
                            "'"+str(area_locality)+"',"
                            "'"+str(coverage_km)+"',"
                            "'"+str(address)+"',"
                            "'"+str(city_id)+"',"
                            "'"+str(worktiming)+"',"
                            "'"+str(multiple_workdays)+"',"
                            "'"+str(homedeliverycost)+"',"
                            "'"+str(notes)+"',"
                            "'"+str(date_of_birth)+"',"
                            "'"+str(pincode)+"',"
                            "'"+str(land_mark)+"',"
                            "'"+str(othershop)+"',"
                            "'"+str(usrid)+"',"
                            "'"+str(service_name)+"'" 
                        ")"
                    )
                    print(f"Create New user details::{insert_query}")
                    cursor.execute(insert_query)
                    
                    insert_login_query = "insert into senior.sadmintbl(type,password,username,usrid) values ('vendor','"+str(password)+"','"+str(username)+"','"+str(usrid)+"')"
                    cursor.execute(insert_login_query)
                connection.commit()

                print("Vendor Added/Updated Successfully.")
                return redirect('dashboard_app:vendors')
        except Exception as e:
            print(f"Error loading data: {e}")

    
   
    query_country = "select countryid,country_name from senior.countrytbl"
    row_country = execute_raw_query(query_country)
    country_data = []
    if not row_country == 500:
        for row in row_country:
            country_data.append({
                'country_id': row[0],
                'country_name': row[1],                
            })
    query_state = "select state_id,state_name from senior.statetbl"
    row_state = execute_raw_query(query_state)
    state_data = []
    if not row_state == 500:
        for row in row_state:
            state_data.append({
                'state_id': row[0],
                'state_name': row[1],                
            })
    query_city = "select city_id,city_name from senior.citytbl"
    row_city = execute_raw_query(query_city)
    city_data = []
    if not row_city == 500:
        for row in row_city:
            city_data.append({
                'city_id': row[0],
                'city_name': row[1],                
            })
            
    query_district = "select district_id,district_name from senior.districttbl"
    row_district = execute_raw_query(query_district)
    district_data = []
    if not row_district == 500:
        for row in row_district:
            district_data.append({
                'district_id': row[0],
                'district_name': row[1],                
            })
    query_taluk = "select taluk_id,taluk_name from senior.taluktbl"
    row_taluk = execute_raw_query(query_taluk)
    taluk_data = []
    if not row_taluk == 500:
        for row in row_taluk:
            taluk_data.append({
                'taluk_id': row[0],
                'taluk_name': row[1],                
            })
    
    # If usrid is provided, retrieve the data for the selected vendor
    context = {}
    data = {}
    print(usrid)
    if usrid:
        error_msg = "No vendor Data Found"
        query = "select vendorid,vendor_name,business_name,manager_or_owner_name,id_proof,shop_type,do_you_home_delivery,area_locality,coverage_km,time_of_opertn,working_days,home_delivery_min_cost,other_notes,mobno,whatsappno,svendortbl.address,age,gender,city_name,taluk_name,district_name,country_name,pincode,land_mark,date_of_birth,state_name,other_shop_type_name,username,password,service_type from senior.sadmintbl,senior.svendortbl,senior.susertbl,senior.citytbl,senior.statetbl,senior.countrytbl,senior.districttbl,senior.taluktbl where svendortbl.cityid=citytbl.city_id and susertbl.usrid=svendortbl.usrid and citytbl.state_id = statetbl.state_id and statetbl.country_id = countrytbl.countryid and citytbl.city_id = districttbl.city_id and districttbl.district_id = taluktbl.district_id and sadmintbl.usrid=svendortbl.usrid  and svendortbl.usrid='"+str(usrid)+"'"
        row = execute_raw_query_fetch_one(query)
        data = []    
        
        if not row == 500:
                 if row:
                    do_you_home_delivery = row[6]
                    if do_you_home_delivery == 1:
                         do_you_home_delivery ='Yes'
                    else:
                         do_you_home_delivery = 'No'
                    data = {
                        'usrid': usrid,
                        'vendorid': row[0],
                        'vendor_name': row[1],
                        'business_name': row[2],
                        'manager_or_owner_name': row[3],
                        'aadharno': row[4],
                        'shop_type': row[5],
                        'do_you_home_delivery': do_you_home_delivery,
                        'area_locality': row[7],
                        'coverage_km': row[8],
                        'work_timing': row[9],
                        'working_days': row[10],
                        'home_delivery_min_cost': row[11],
                        'other_notes': row[12],
                        'mobno': row[13],
                        'whatsappno': row[14],
                        'address': row[15],
                        'age': row[16],
                        'gender': row[17],
                        'city_name': row[18],
                        'taluk_name': row[19],
                        'district_name': row[20],
                        'country_name': row[21],
                        'pincode': row[22],
                        'landmark': row[23],
                        'dateofbirth': row[24],
                        'state_name': row[25],
                        'other_shop_type_name': row[26],
                        'username': row[27],
                        'password': row[28],
                        'service_type':row[29],
                    }
                    
       
        else:
            error_msg = 'Something Went Wrong. [Please Try after sometime ]'
            
       
   
    
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    context = {
        'data': data,
        'all_days':all_days,
        'country_data': country_data,
        'state_data': state_data,
        'city_data': city_data,
        'district_data': district_data,
        'taluk_data': taluk_data,
        }        
    return render(request,'admin_pages/add_vendor.html',context)

def create_new_service_request(request):
    error_code = "No senior citizen found with this number"
    print(error_code)
    if request.method == "POST":
        primary_no = request.POST.get('primary_no')
        service_name = request.POST.get('service_name')
        sub_service_name = request.POST.get('sub_service_name')
        if_other_service_name = request.POST.get('other_service')
        allopathy_type = request.POST.get('allopathy_type')
        feedback = request.POST.get('feedback')
        seva_mitra_desc = request.POST.get('seva_mitra')
        if not feedback:
            feedback = 'NA'
        if not if_other_service_name:
            if_other_service_name = 'NA'
        if allopathy_type == 'Select Allopathy':
            allopathy_type = 'NA'
        if not seva_mitra_desc:
            seva_mitra_desc = 'NA'
        if not sub_service_name:
            error_code = "Please Provide Service Type Sub Category"
            context = {
                    'error':error_code,
                    'primary_no':primary_no,
                    'service_name':service_name,
                    'other_service':if_other_service_name,
                    'allopathy_type':allopathy_type,
                    'feedback':feedback,
                    'seva_mitra':seva_mitra_desc
                }
            return render(request,'admin_pages/create_new_service_request.html',context)
                
        query = "select usrname,susertbl.gender,susertbl.address,susertbl.age,seniorid from senior.senior_citizens,senior.susertbl where senior_citizens.usrid=susertbl.usrid and mobno='"+str(primary_no)+"'"
        row = execute_raw_query_fetch_one(query)
        if not row == 500:
            usrname = row[0]
            gender = row[1]
            address = row[2]
            age = row[3]
            senior_id = row[4]
            
            try:
                with connection.cursor() as cursor:
                    
                    
                    insert_query = (
                        "insert into senior.sservice_tbl (senior_id,senior_name,service_name,if_other_name,allopathy_type,feedback,seva_mitra_descp,sub_service_name)"
                        "values ('"+str(senior_id)+"','"+str(usrname)+"','"+str(service_name)+"','"+str(if_other_service_name)+"','"+str(allopathy_type)+"','"+str(feedback)+"','"+str(seva_mitra_desc)+"','"+str(sub_service_name)+"') returning serviceid"
                    )
                    print(f"Create New Service details::{insert_query}")
                    cursor.execute(insert_query)
                    serviceid = cursor.fetchone()[0]
                    connection.commit()
                    
                    def select_vendors_to_assign_service_request():
                        error_msg = 'No Vendors Found who provide this service'
                        query = "select vendorid,vendor_name,business_name,svendortbl.usrid,shop_type,other_shop_type_name from senior.susertbl,senior.svendortbl where svendortbl.usrid=susertbl.usrid and service_type='"+str(service_name)+"'"#or other_shop_type_name='"+str(other_type)+"'
                        query_result = execute_raw_query(query)
                        if not query_result == 500 and not query_result == 400:
                            for row in query_result:
                                vendorid = row[0]
                                vendor_name = row[2]
                               
                                send_notifications_to_vendors_for_service_request(request,vendorid,vendor_name,serviceid)
                            
                            time.sleep(60)  # Wait for 2 minutes (120 seconds)
                            assign_order_to_vendor(request,serviceid)       
                        else:
                            error_msg = 'Something Went Wrong'
                        if not query_result:
                            print('No Vendors found of the category')
                        return
                    # Create a thread to execute the delayed function
                    t = threading.Timer(10, select_vendors_to_assign_service_request)
                    t.start()
                    
                    print("Service Created Successfully.")
                    return redirect('dashboard_app:services')
            except Exception as e:
                print(f"Error loading data: {e}")
                error_code = "Something Went wrong please try after sometime"
                context = {
                    'error':error_code,
                    'primary_no':primary_no,
                    'service_name':service_name,
                    'other_service':if_other_service_name,
                    'allopathy_type':allopathy_type,
                    'feedback':feedback,
                    'seva_mitra':seva_mitra_desc
                }
                return render(request,'admin_pages/create_new_service_request.html',context)
        else:
            context = {
                'error':error_code,
                'primary_no':primary_no,
                'service_name':service_name,
                'other_service':if_other_service_name,
                'allopathy_type':allopathy_type,
                'feedback':feedback,
                'seva_mitra':seva_mitra_desc
            }
            return render(request,'admin_pages/create_new_service_request.html',context)
            
    return render(request,'admin_pages/create_new_service_request.html')


def all_service_requests(request):
    error_msg = "No Service Request Found"
    query = "select senior_id,senior_name,service_name,serviceid,if_other_name,allopathy_type,feedback,seva_mitra_descp,primary_mobno,usrid,address,create_at,sub_service_name,gender,age from senior.senior_citizens,senior.sservice_tbl where senior_citizens.seniorid=sservice_tbl.senior_id"
    
    query_result = execute_raw_query(query)
   
    data = []    
    if not query_result == 500 and not query_result == 400:
        for row in query_result:
            create_at = row[11]
            formatted_date = epoch_to_time(create_at)
            data.append({
                'senior_id': row[0],
                'senior_name': row[1],
                'service_name': row[2],
                'serviceid': row[3],
                'if_other_name': row[4],
                'allopathy_type': row[5],
                'feedback': row[6],
                'seva_mitra_descp': row[7],
                'primary_mobno': row[8],
                'usrid': row[9],
                'address': row[10],
                'create_at':formatted_date,
                'sub_service_name':row[12],
                'age':row[13],
                'gender':row[14],
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return render(request,'admin_pages/all_service_requests.html',context)


'''
TODO: Service 101 ///Medicine Delivery/ Grocery / Fresh Produce/ Document Pickup
SELECT ALL VENDORS WITH THE FOLLOWING CATEGORY
#select vendorid,vendor_name,business_name,svendortbl.usrid,shop_type,other_shop_type_name from senior.susertbl,senior.svendortbl where svendortbl.usrid=susertbl.usrid and shop_type='General Store' or other_shop_type_name='Pharmacy';
SEND NOTIFICATION TO VENDORS WHO ARE IN THAT AREA
#insert into senior.notification_tbl(title,description,service_id,sender_id,reciever_id) values ()
wait for 2 mins
##[Select Query to check order is accepted or not by anyone]check in service table if the order is assigned to anyone first to avoid multiple vendor accepting same order
#If Accepted by Anyone then add in service_history tbl 'Assigned'

START PROCESSING WHEN VENDOR START PREPARING THE ORDER
#then add in service_history tbl 'Out for delivery'
Delivered
#then add in service_history tbl 'Delivered'
Vendor will change status to task completed
'''

 
def send_notifications_to_vendors_for_service_request(request,vendorid,vendor_name,serviceid):
    try:
        with connection.cursor() as cursor:
            # Insert Record in notification table 
            title = "Service Request"
            description = ""
            notify_query = "insert into senior.notification_tbl(title,description,service_id,sender_id,reciever_id) values ('"+str(title)+"','"+str(description)+"','"+str(serviceid)+"','1','"+str(vendorid)+"')"
            cursor.execute(notify_query)
            
            connection.commit()

            print(f'Notifications Send to {vendor_name}[{vendorid}] for service_id:[{serviceid}]')
    except Exception as e:
        print(f"Error sending vendor notification {e}")  
    
    return   

def assign_order_to_vendor(request,serviceid):
    query = "select senior_id,senior_name,service_name,if_other_name,allopathy_type,seva_mitra_descp,sub_service_name from senior.sservice_tbl where status!='Assigned' and serviceid='"+str(serviceid)+"'"
    query_result = execute_raw_query_fetch_one(query)
    if not query_result == 500 and not query_result == 400:
        print('Order Assigned to other vendor already. So Please accept other orders')
        return
    elif not query_result == 400 :
        try:
            query = "select service_name,if_other_name,vendor_id from senior.sservice_tbl where serviceid='"+str(serviceid)+"' and vendor_id!='-1'"
            result = execute_raw_query_fetch_one(query)
            if not result == 500 and not result == 400:
                service_type = result[0]
                service_type2 = result[1]
                vendorid = result[2]
                if not service_type2 == 'NA':
                 service_type = service_type2
                with connection.cursor() as cursor:
                # Assign Order to Vendor
                    insert_query = "insert into senior.service_historytbl(serviceid,service_type,vendor_id,status) values ('"+str(serviceid)+"','"+str(service_type)+"','"+str(vendorid)+"','Assigned')"
                    cursor.execute(insert_query)
                
                    connection.commit()
                    print(f"Service Assigned to vendor successfully!.")
            else:
                print('Order not accepted by anyone')
                #TODO:Need to send again to different vendor
                return
        except Exception as e:
            print(f"Error Assigning Order to Vendor: {e}")
    else:
        print('No Vendor Registrated with this Service')
        return
            

def delete_senior_citizen(request, usrid):
    try:
        with connection.cursor() as cursor:
            # Delete the senior citizen using usrid
            delete_query = "DELETE FROM senior.senior_citizens WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_query)
            delete_user_query = "DELETE FROM senior.susertbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_user_query)
            connection.commit()

            print(f"Senior Citizen with usrid {usrid} deleted successfully.")
    except Exception as e:
        print(f"Error deleting senior citizen: {e}")

    return redirect('dashboard_app:senior_citizens')

def delete_volunteer(request, usrid):
    try:
        with connection.cursor() as cursor:
            # Delete the senior citizen using usrid
            delete_query = "DELETE FROM senior.svolunteerstbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_query)
            delete_user_query = "DELETE FROM senior.susertbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_user_query)
            connection.commit()

            print(f"Volunteer with usrid {usrid} deleted successfully.")
    except Exception as e:
        print(f"Error deleting volunteer: {e}")

    return redirect('dashboard_app:volunteers')

def delete_vendor(request, usrid):
    try:
        with connection.cursor() as cursor:
            # Delete the senior citizen using usrid
            delete_query = "DELETE FROM senior.svendortbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_query)
            delete_user_query = "DELETE FROM senior.susertbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_user_query)
            connection.commit()

            print(f"Vendor with usrid {usrid} deleted successfully.")
    except Exception as e:
        print(f"Error deleting vendor: {e}")

    return redirect('dashboard_app:vendors')


def execute_raw_query(query, params=None,):
    
    result = []
    try:
        print(f"{Fore.GREEN}Query Executed: {query}{Style.RESET_ALL}")
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
            print(f"Result: {result}, Result length: {len(result)}")
        return result
    except DatabaseError as e:
        print(f"{Fore.RED}DatabaseError Found: {e}{Style.RESET_ALL}")
        # Need To Handle the error appropriately, such as logging or raising a custom exception
        # roll back transactions if needed
        
        return 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle other unexpected errors
        return 500
    finally:
        # Ensure the cursor is closed to release resources
        cursor.close()  # Note: cursor might not be defined if an exception occurs earlier

def execute_raw_query_fetch_one(query, params=None,):
    
    result = []
    try:
        print(f"{Fore.GREEN}Query Executed: {query}{Style.RESET_ALL}")
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            print(f"Result: {result}, Result length: {len(result)}")
        return result
    except DatabaseError as e:
        print(f"{Fore.RED}DatabaseError Found: {e}{Style.RESET_ALL}")
        # Need To Handle the error appropriately, such as logging or raising a custom exception
        # roll back transactions if needed
        
        return 500
    except TypeError as e:
        print(f'NoneType No Data Found:: {e}')
        return 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle other unexpected errors
        return 500
    finally:
        # Ensure the cursor is closed to release resources
        cursor.close()  # Note: cursor might not be defined if an exception occurs earlier

def custom_404_view(request, exception):
    return render(request, 'error_pages/404.html', status=404)


def custom_500_view(request):
    return render(request, 'error_pages/500.html', status=500)


def isLoggedIn(request):
    return request.session.get('is_logged_in',False)

def epoch_to_time(epoch):
    datetime_obj = datetime.utcfromtimestamp(epoch)
    gmt_plus_0530 = pytz.timezone('Asia/Kolkata')
    datetime_obj_gmt_plus_0530 = datetime_obj.replace(tzinfo=pytz.utc).astimezone(gmt_plus_0530)
    formatted_datetime = datetime_obj_gmt_plus_0530.strftime('%Y-%m-%d %I:%M:%S %p')
    return formatted_datetime
