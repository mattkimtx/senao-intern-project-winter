from django.http import JsonResponse
from .mongo import mongoDB
from datetime import datetime
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
                    data = json.loads(request.body.decode('utf-8'))
                    username = data['username']
                    password = data['password']
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
     
def user_login(request):
     try:
          if request.method == 'GET':
               try:
                    data = json.loads(request.body.decode('utf-8'))
                    username = data['username']
                    password = data['password']
               except KeyError:
                    return JsonResponse({'success': 'false', 
                                         'error': 'username and password are required fields'}, status=400)

               # gets timestamp from the request
               timestamp = datetime.now()

               # Creates MongoDB object
               users_db = mongoDB()

               # verify login
               if users_db.user_exists(username) == False: # if username doesn't exist
                    users_db.close()
                    return JsonResponse({'success': 'false', 
                                         'error': 'Username does not exist'}, status=400)
               else: # username exists
                    # if logged in too many times
                    if users_db.check_failed_login_attempts(username, timestamp) == False:
                         # too many failed attempts
                         users_db.close()
                         return JsonResponse({'success': 'false', 
                                              'error': 'Too many failed login attempts, please wait 1 minute until trying again'}, status=400)
                    # successful login
                    if users_db.password_exists(username, password):
                         users_db.close()
                         return JsonResponse({'success': 'true',
                                              'error': 'none'}, status=200)
                    # failed to login, will add another failed login to counter
                    else:
                         users_db.failed_login(username, timestamp)
                         users_db.close()
                         return JsonResponse({'success': 'false', 
                                              'error': 'Invalid username or password'}, status=400)
          else:
               return JsonResponse({'success': 'false', 
                                    'error': 'invalid HTTP method'}, status=405)
     
     except Exception:
          return JsonResponse({'success': 'false', 
                               'error': 'an error occured'}, status=500) 