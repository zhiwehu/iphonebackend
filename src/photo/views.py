
from django.shortcuts import render_to_response
from django.template import RequestContext

def home(request,
         template='site_base.html',
         extra_context=None):

    context = {}

    if extra_context:
        context.update(extra_context)

    return render_to_response(template, context, context_instance=RequestContext(request))



'''
def signin(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

def signup(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    birthday = request.POST.get('birthday')
    gender = request.POST.get('gender')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    avatar_url = request.POST.get('avatar_url')

def get_user_today_photo(request):
    user_id = request.GET.get('user')

def get_popular_photo(request):
    pass
'''