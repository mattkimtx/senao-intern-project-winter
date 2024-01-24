from django.http import JsonResponse
from .mongo import mongoDB
from datetime import datetime
from django.contrib.auth import authenticate
import json
import re

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
          user = authenticate(request, username=username, password=password) 
          # read json document to see if request was valid
          read_json = json.loads(user.content)
          success = read_json['success']
          # authentication was successful   
          if success == 'true':
               return JsonResponse({'success': 'true',
                                        'error': 'none'}, status=200)
          # authentication failed, return json packet from authentication
          else:
               return user
     else:
          return JsonResponse({'success': 'false', 
                               'error': 'invalid HTTP method'}, status=405)