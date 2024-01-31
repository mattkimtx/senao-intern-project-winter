from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from .mongo import mongoDB
from datetime import datetime
from django.contrib.auth import authenticate
from functools import wraps
import secrets
import json
import re
# optimization testing
import time

# password complexity requirement (uppercase, lowercase, number, special character)
def valid_password(password):
     return bool(re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)', password))

def user_signup(request):
     try:
          # HTTP Method
          if request.method == 'POST':    
               try:
                    username = request.POST.get('username', '')
                    password = request.POST.get('password', '')
               except KeyError:
                    return JsonResponse({'success': 'false', 
                                         'error': 'username and password are required fields'}, status=400)
               
               # check if username and password are valid
               if len(username) < 4 or len(username) > 32:
                    return JsonResponse({'success': 'false', 
                                         'error': 'Username length must be between 3-32 characters'}, status=400) # 400 is fail length requirement
               if len(password) < 8 or len(password) > 32:
                    return JsonResponse({'success': 'false',
                                         'error': 'Password length must be between 8-32 characters'}, status=400)
               if valid_password(password) == False:
                    return JsonResponse({'success': 'false', 
                                         'error': 'Password must contain at least one uppercase, lowercase, and number'}, status=400) # syntax not correct

               # Creates MongoDB object
               users_db = mongoDB()
               
               # check if username already exists
               if users_db.user_exists(username):
                    users_db.close()
                    return JsonResponse({'success': 'false', 
                                         'error': 'Username already exists'}, status=400)
               else:
                    try:
                         users_db.create_account(username, password)
                         users_db.close()
                         return JsonResponse({'success': 'true',
                                             'error': 'none'}, status=200)
                    except Exception:
                         users_db.close()
                         return JsonResponse({'success': 'false', 
                                              'error': 'An error occured while creating the account'}, status=500)
               
          else:
               return JsonResponse({'success': 'false', 
                                    'error': 'invalid HTTP method'}, status=405) 

     except Exception:
          return JsonResponse({'success': 'false', 
                               'error': 'an error occured'}, status=500)

# just need to create a new login function to incorporate Django authentication API
def user_login(request):
     if request.method == 'GET':
          username = request.GET.get('username', '')
          password = request.GET.get('password', '')
          # create MongoDB object
          users_db = mongoDB()
          user = authenticate(request, username=username, password=password, users_db=users_db) 
          # read json document to see if request was valid
          read_json = json.loads(user.content)
          success = read_json['success']
          print(success)
          # authentication was successful   
          if success == 'true':
               print(1)
               # create a session token
               session_token = secrets.token_hex(16)
               # update the session token in the database
               users_db.create_session_token(username, session_token)
               
               response = JsonResponse({'success': 'true',
                                        'error': 'none',
                                        'session_token': session_token}, status=200)

               return response
          # authentication failed, return json packet from authentication
          else:
               return user
     else:
          return JsonResponse({'success': 'false', 
                               'error': 'invalid HTTP method'}, status=405)

# instead of using Django's login_required
def custom_login_required(view_func):
     @wraps(view_func)
     def _wrapped_view(request, *args, **kwargs):
          session_token = request.COOKIES.get('session_token')

          if session_token and session_is_valid(session_token):
               return view_func(request, *args, **kwargs)

          return HttpResponseForbidden("Access Denied")  # Return a forbidden response

     return _wrapped_view

def session_is_valid(session_token):
     users_db = mongoDB()

     # Check if the session token exists in the database
     return users_db.session_token_exists(session_token)

# def custom_login_required(view_func):
#      @wraps(view_func)
#      def _wrapped_view(request, *args, **kwargs):
#           session_token = request.COOKIES.get('session_token')
#           if session_token and session_is_valid(session_token):  # Implement your session validation logic
#                return view_func(request, *args, **kwargs)  # User is authenticated; proceed to the view
        
#           return render(request, 'account/login.html')  # JsonResponse({'message': 'Access Denied'}, status=401)
    
#      return _wrapped_view

# def session_is_valid(session_token):
#      users_db = mongoDB()
#      # check if session token exists in database
#      if users_db.session_token_exists(session_token):
#           return True
#      else:
#           return False
     
def user_logout(request):
     users_db = mongoDB()
     session_token = request.COOKIES.get('session_token')
     users_db.delete_session_token(session_token)
     return JsonResponse({'success': 'true',
                          'error': 'none'}, status=200)