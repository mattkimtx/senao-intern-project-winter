from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth import logout, login
from api_account_password.act_pwd_api import user_login, user_signup
import json

@csrf_exempt
def signup_attempt(request):
    json_response = user_signup(request)

    # convert into easy to read python dictionary
    read_json = json.loads(json_response.content)
    # read json document to see if request was valid
    success = read_json['success']
    print(success)
    error = {'error' : read_json['error']}

    # two cases. 1st, login successful; 2nd, login failed
    if success == 'true':
        return redirect('account/login.html')
    else:
        return render(request, 'account/signup.html', error)
    
@csrf_exempt
def login_attempt(request):
    json_response = user_login(request)

    # convert into easy to read python dictionary
    read_json = json.loads(json_response.content)
    # read json document to see if request was valid
    success = read_json['success']
    error = {'error' : read_json['error']}

    # two cases. 1st, login successful; 2nd, login failed
    if success == 'true':
        return render(request, 'selectApp/index.html', error)
    else:
        return render(request, 'account/login.html', error)
    
def signup_view(request):
    return render(request, 'account/signup.html')

def login_view(request):
    return render(request, 'account/login.html')

def index_view(request):
    return render(request, 'account/index.html')

@csrf_exempt
def logout_view(request):
    logout(request)
    return render(request, 'account/logout.html')