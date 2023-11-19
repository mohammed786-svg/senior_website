from django.shortcuts import render, redirect, reverse
from django.db import connection, DatabaseError
from django.contrib.auth import logout
from django.http import HttpResponseServerError,JsonResponse
from colorama import Fore, Style
from django.utils import timezone
from datetime import datetime
import pytz
# Create your views here.

def login_view(request):
    print("Vendor Login View ")
    alert_message = None
    if request.method == "POST":
        username = request.POST.get('uname')
        password = request.POST.get('passwrd')
        query = "select sadmintbl.usrid,username,password,vendorid from senior.svendortbl,senior.sadmintbl where sadmintbl.usrid=svendortbl.usrid and username='"+str(username)+"' and password='"+str(password)+"'"
        print("query::"+str(query))
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                user_data = cursor.fetchone()

            if user_data and user_data[2]:
                # User is authorized
                print(user_data[0])
                request.session['vuser_id'] = user_data[0]
                request.session['vusername'] = user_data[1]
                request.session['vpassword'] = user_data[2]
                request.session['vendorid'] = user_data[3]
                request.session['is_logged_in_vendor'] = True
                # Setting the session to expire after one day (86400 seconds)
                request.session.set_expiry(86400)
                
                return redirect('vendor_app:dashboard')
            else:
                # If the login is unsuccessful, store the form data in the context
                context = {
                'username': username,
                'password': password,
                'error_message': 'Invalid credentials',  # You can customize this error message
                }
                return render(request, 'login.html', context)
            
            
        except Exception as e:
            # Handle database-related exceptions here
            alert_message = f"An error occurred: {str(e)}"
    
    return render(request,"main_pages/login.html",{'error_message': alert_message})


def dashboard(request):
    print('Vendor Dashboard new')
    loggedIN = isLoggedIn(request)
    if loggedIN == False:
        return redirect('vendor_app:login')
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    return render(request, 'main_pages/dashboard_vendor.html', {'current_url': current_url})

def profile(request):
    usrid = request.session.get('vuser_id')
    print(f'usrid::{usrid}')
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
                            "other_shop_type_name='"+str(othershop)+"'"
                            " where usrid='"+str(usrid)+"'"
                        
                    )
                    print(f"update user details::{update_query}")
                    cursor.execute(update_query)
                    update_login_query = "update senior.sadmintbl set password='"+str(password)+"', username='"+str(username)+"' where usrid='"+str(usrid)+"'";
                    cursor.execute(update_login_query)
                    connection.commit()

                print("Vendor Profile Details Updated Successfully.")
                return redirect('vendor_app:dashboard')
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
        query = "select vendorid,vendor_name,business_name,manager_or_owner_name,id_proof,shop_type,do_you_home_delivery,area_locality,coverage_km,time_of_opertn,working_days,home_delivery_min_cost,other_notes,mobno,whatsappno,svendortbl.address,age,gender,city_name,taluk_name,district_name,country_name,pincode,land_mark,date_of_birth,state_name,other_shop_type_name,username,password from senior.sadmintbl,senior.svendortbl,senior.susertbl,senior.citytbl,senior.statetbl,senior.countrytbl,senior.districttbl,senior.taluktbl where svendortbl.cityid=citytbl.city_id and susertbl.usrid=svendortbl.usrid and citytbl.state_id = statetbl.state_id and statetbl.country_id = countrytbl.countryid and citytbl.city_id = districttbl.city_id and districttbl.district_id = taluktbl.district_id and sadmintbl.usrid=svendortbl.usrid  and svendortbl.usrid='"+str(usrid)+"'"
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
                        
                    }
                    
       
        else:
            error_msg = 'Something Went Wrong. [Please Try after sometime ]'
            
       
   
    
    all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_url = request.get_full_path()
    
    context = {
        'data': data,
        'all_days':all_days,
        'country_data': country_data,
        'state_data': state_data,
        'city_data': city_data,
        'district_data': district_data,
        'taluk_data': taluk_data,
        'current_url': current_url
        }        
    return render(request,'main_pages/profile.html',context)


def all_orders(request):
    
    loggedIN = isLoggedIn(request)
    if loggedIN == False:
        return redirect('vendor_app:login')
    vendor_id = request.session.get('vendorid')
    query = "select serviceid,senior_id,senior_name,service_name,if_other_name,allopathy_type,feedback,sub_service_name,create_at,date,status from senior.sservice_tbl where vendor_id='"+str(vendor_id)+"'"
    row_orders = execute_raw_query(query)
    data = []
    error_msg="No Orders Found"
    if not row_orders == 500:
        for row in row_orders:

            create_at= row[8]
            time = epoch_to_time(create_at)
            data.append({
                'service_id': row[0],
                'senior_id': row[1],
                'senior_name': row[2],
                'service_name': row[3],
                'if_other_name': row[4],
                'allopathy_type': row[5],
                'feedback': row[6],
                'sub_service_name': row[7],
                'create_at': time,
                'date': row[9],
                'status': row[10],
            })
    else:
         error_msg="Something went wrong"
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {
            'current_url': current_url,
            'data':data,
            'error_msg':error_msg
            }
    return render(request, 'main_pages/orders.html', context)

def update_notification(request,service_id=None):
    error = False
    loggedIN = isLoggedIn(request)
    if loggedIN == False:
        return redirect('vendor_app:login')
    current_url = request.get_full_path()
    if request.method == "POST":
        print('accept the order')
        #To Prevent User From Accepting Service if the service is already assigned.
        query = "select senior_id,senior_name,service_name,if_other_name,allopathy_type,seva_mitra_descp,sub_service_name from senior.sservice_tbl where status='Assigned' and serviceid='"+str(service_id)+"'"
        query_result = execute_raw_query_fetch_one(query)
        if not query_result == 500 and not query_result == 400:
            print('Order Assigned to other vendor already. So Please accept other orders')
            context = {
                    'current_url': current_url,
                    'error':error,        
                    }
            return render(request, 'main_pages/notifications.html', context) 

        
        if service_id:
            try:
                 vendorid = request.session.get('vendorid')
                 with connection.cursor() as cursor:
                        # Assign Order to Vendor
                        insert_query = "insert into senior.order_accepttbl(service_id,vendor_id,status,seen_status) values ('"+str(service_id)+"','"+str(vendorid)+"','Accepted','1')"
                        cursor.execute(insert_query)
                        #Update Status to assigned in senior.sservicetbl
                        update_query = "update senior.sservice_tbl set status='Assigned',vendor_id='"+str(vendorid)+"'"
                        cursor.execute(update_query)
                        connection.commit()
                        print(f"Vendor Accepted Order successfully!.")
                        return redirect('vendor_app:orders')
            except Exception as e:
                    print(f"Error Assigning Order to Vendor: {e}")
                
    
    # using the 'current_url' variable to determine the active card.
    #reciever ID will be vendor ID
    vendorid = request.session.get('vendorid')
    data = {}
    old_notification_data = {}
    ret_error = "No Notifications Found Till Now"
    todayDate = getTodaysDate()
    query = "select title,description,service_id from senior.notification_tbl where reciever_id='"+str(vendorid)+"' order by notifyid desc"
    result = execute_raw_query_fetch_one(query)
    if not result == 500 and not result == 400:
        if result:
            service_id=result[2]
            query_order = "select vendor_id from senior.order_accepttbl where service_id='"+str(service_id)+"' and seen_status='1'"
            result2 = execute_raw_query_fetch_one(query_order)
            if not result2 == 500 and not result2 == 400:
                context = {
                    'current_url': current_url,
                    'error':True,        
                    }
                query_record = " select order_accepttbl.service_id,time,dt,service_name,senior_name,order_accepttbl.status from senior.sservice_tbl,senior.order_accepttbl where order_accepttbl.service_id=sservice_tbl.serviceid and order_accepttbl.vendor_id='"+str(vendorid)+"'"
                ret = execute_raw_query(query_record)
                
              
                if not ret == 500:
                    for row in ret:
                        time = row[1]
                        formatted_date = epoch_to_time(time)
                        old_notification_data = {
                            'nserviceid':row[0],
                            'mtime':formatted_date,
                            'ndate':row[2],
                            'nservice_name':row[3],
                            'nsenior_name':row[4],
                            'nstatus':row[5],
                            
                        }
                else:
                    ret_error = "Something went wrong !"
                
                context = {
                    'current_url': current_url,
                    'error':True, 
                    'ret_error':ret_error,
                    'old_notify':old_notification_data,
                    'todayDT':todayDate          
                    }
                return render(request, 'main_pages/notifications.html', context) 
            query2 = "select senior_name,senior_id,service_name,if_other_name from senior.sservice_tbl where serviceid='"+str(service_id)+"'"
            res = execute_raw_query_fetch_one(query2)
            if not res == 500:
                seniorid = res[1]
                #To Get Senior Citizen Information
                query3 = "select primary_mobno,address,state,city,district,taluk,pincode,land_mark,house_no from senior.senior_citizens where seniorid='"+str(seniorid)+"'"
                res3 = execute_raw_query_fetch_one(query3)
                if not res3 == 500:
                    data = {
                        'senior_name':res[0],
                        'senior_id':seniorid,
                        'service_name':res[2],
                        'if_other_name':res[3],
                        'title':result[0],
                        'description':result[1],
                        'service_id':result[2],
                        'primary_mobno':res3[0],
                        'address':res3[1],
                        'state':res3[2],
                        'city':res3[3],
                        'district':res3[4],
                        'taluk':res3[5],
                        'pincode':res3[6],
                        'land_mark':res3[7],
                        'house_no':res3[8],
                    } 
    
    context = {
            'current_url': current_url,
            'data':data,
            'error':error,
            'ret_error':ret_error,
            'old_notify':old_notification_data,
            'todayDT':todayDate        
        }
    return render(request, 'main_pages/notifications.html', context)


#Vendor will accept the order here
# def order_accept(request):
#     print('Accepting Order')
#     if request.method == "POST":
#         service_id = request.POST.get('serviceid')
#         try:
#              vendorid = request.session.get('vendorid')
#              with connection.cursor() as cursor:
#                     # Assign Order to Vendor
#                     insert_query = "insert into senior.order_accepttbl(service_id,vendor_id) values ('"+str(service_id)+"','"+str(vendorid)+"')"
#                     cursor.execute(insert_query)
#                     #Update Status to assigned in senior.sservicetbl
#                     update_query = "update senior.sservice_tbl set status='Assigned',vendor_id='"+str(vendorid)+"'"
#                     cursor.execute(update_query)
#                     connection.commit()
#                     print(f"Vendor Accepted Order successfully!.")
#         except Exception as e:
#                 print(f"Error Assigning Order to Vendor: {e}")
#     return render(request,'main_pages/order_success.html',{'isSuccess':True})

def isLoggedIn(request):
    return request.session.get('is_logged_in_vendor',False)

def epoch_to_time(epoch):
    datetime_obj = datetime.utcfromtimestamp(epoch)
    gmt_plus_0530 = pytz.timezone('Asia/Kolkata')
    datetime_obj_gmt_plus_0530 = datetime_obj.replace(tzinfo=pytz.utc).astimezone(gmt_plus_0530)
    formatted_datetime = datetime_obj_gmt_plus_0530.strftime('%Y-%m-%d %I:%M:%S %p')
    return formatted_datetime


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
        return 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle other unexpected errors
        return 500
    finally:
        # Ensure the cursor is closed to release resources
        cursor.close()  # Note: cursor might not be defined if an exception occurs earlier

from datetime import date
def getTodaysDate():
    today_date = date.today()
    return today_date.strftime('%Y-%m-%d')
