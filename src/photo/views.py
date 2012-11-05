from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from models import Photo, Avatar
from tastypie.authentication import BasicAuthentication

def home(request,
         template='site_base.html',
         extra_context=None):

    context = {}

    if extra_context:
        context.update(extra_context)

    return render_to_response(template, context, context_instance=RequestContext(request))


@csrf_exempt
def api_upload_photo(request):
    if request.method == 'POST':
        basic_auth = BasicAuthentication()
        if basic_auth.is_authenticated(request):
            photo = Photo(user=request.user, title=request.POST.get('title', None), file=request.FILES['file'])
            photo.save()

            response_data={"file_url": photo.file.url}
            return HttpResponse(simplejson.dumps(response_data), mimetype='application/json')
    raise Http404


@csrf_exempt
def api_upload_avatar(request):
    if request.method == "POST":
        file = request.FILES['file']
        avatar = Avatar(file=file)
        avatar.save()
        response_data={"file_url": avatar.file.url}
        return HttpResponse(simplejson.dumps(response_data), mimetype='application/json')
    raise Http404

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