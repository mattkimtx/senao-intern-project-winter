from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .act_pwd_api import user_login, user_signup
from django.views import generic

@csrf_exempt
def signup(request):
    json_data = user_signup(request)
    return json_data

@csrf_exempt
def login(request):
    json_data = user_login(request)
    return json_data

class loginPage(generic.ListView):
    template_name = 'account/login.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return None