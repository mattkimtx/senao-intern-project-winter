from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from .act_pwd_api import user_login, user_signup
from .convert_WGSI import convert_to_json, convert_to_json_post
import json

@csrf_exempt
def signup_attempt(request):
    # json_file = convert_to_json_post(request)
    # print(json.loads(json_file.content)) 
    json_response = user_signup(request)

    # convert into easy to read python dictionary
    read_json = json.loads(json_response.content)
    # read json document to see if request was valid
    success = read_json['success']
    error = {'error' : read_json['error']}

    # two cases. 1st, login successful; 2nd, login failed
    if success == 'true':
        return render(request, 'selectApp/login.html', error)
    else:
        return render(request, 'account/signup.html', error)
    
def signup(request):
    return render(request, 'account/signup.html')
    
@csrf_exempt
def login_attempt(request):
    # load json document
    json_file = convert_to_json(request)
    print(json.loads(json_file.content)) 
    json_response = user_login(json_file)
    print(json.loads(json_response.content))

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

def login(request):
    return render(request, 'account/login.html')

def index(request):
    return render(request, 'account/login.html')