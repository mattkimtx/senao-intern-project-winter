from django.contrib.auth.backends import BaseBackend
from django.http import JsonResponse
from datetime import datetime
from api_account_password.mongo import mongoDB


class MyBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, users_db=mongoDB()):
          # get timestamp from the request andc create MongoDB object
          timestamp = datetime.now()
          # verify login
          if users_db.user_exists(username) == False: # if username doesn't exist
               return JsonResponse({'success': 'false', 
                                        'error': 'invalid username'}, status=400)
          else: # username exists
               # if logged in too many times
               if users_db.check_failed_login_attempts(username, timestamp) == False:
                    # too many failed attempts
                    return JsonResponse({'success': 'false', 
                                             'error': 'Too many failed login attempts, please wait 1 minute until trying again.'}, status=400)
               # successful login
               if users_db.password_exists(username, password):
                    return JsonResponse({'success': 'true',
                                         'error': 'none'}, status=200)
               # failed to login, will add another failed login to counter
               else:
                    users_db.failed_login(username, timestamp)
                    return JsonResponse({'success': 'false', 
                                             'error': 'invalid username or password'}, status=400)