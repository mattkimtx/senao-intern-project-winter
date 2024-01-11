import json
from django.http import JsonResponse

def convert_to_json(request):
    # Extract data from the GET request
    username = request.GET.get('username', '')
    password = request.GET.get('password', '')

    # Return the JSON response
    return JsonResponse({'username': username,
                         'password': password,})

def convert_to_json_post(request):
     # Extract data from the POST request
     username = request.POST.get('username', '')
     password = request.POST.get('password', '')
     
     # Return the JSON response
     return JsonResponse({'username': username,
                          'password': password,})