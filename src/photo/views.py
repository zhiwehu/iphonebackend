import urllib
from allauth.socialaccount import providers, requests
from allauth.socialaccount.helpers import complete_social_login, render_authentication_error
from allauth.socialaccount.models import SocialToken, SocialLogin, SocialAccount
from allauth.socialaccount.providers import oauth
from allauth.socialaccount.providers.facebook.forms import FacebookConnectForm
from allauth.socialaccount.providers.facebook.provider import FacebookProvider
from allauth.socialaccount.providers.facebook.views import fb_complete_login
from allauth.socialaccount.providers.oauth.client import OAuthError
from allauth.socialaccount.providers.twitter.provider import TwitterProvider
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

from models import Photo, Avatar, Message
from oauth2 import Token, Consumer, Client
from photo.api import UserResource
from utils import get_photo_info
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

            at_users = request.POST.get('atusers', '').split(',')
            for user_id in at_users:
                try:
                    to_user = User.objects.get(id=int(user_id))
                    message = Message(from_user=request.user, to_user=to_user, description=get_photo_info(photo)).save()
                except Exception:
                    pass

            # TODO the api resource_uri need to dynamic
            response_data={"resource_uri": "/api/v1/photo/%d/" % (photo.id) , "file_url": photo.file.url}
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


@csrf_exempt
def api_user_unfollow(request):
    if request.method == 'POST':
        basic_auth = BasicAuthentication()
        if basic_auth.is_authenticated(request):
            to_user_id = int(request.POST.get("to_user", 0))
            try:
                to_user = User.objects.get(id=to_user_id)
            except User.DoesNotExist:
                raise Http404
            from_user = request.user
            from_user.relationships.remove(to_user)

            response_data={'status':'success'}
            return HttpResponse(simplejson.dumps(response_data), mimetype='application/json')
    raise Http404


@csrf_exempt
def api_user_follow(request):
    if request.method == 'POST':
        basic_auth = BasicAuthentication()
        if basic_auth.is_authenticated(request):
            to_user_id = int(request.POST.get("to_user", 0))
            try:
                to_user = User.objects.get(id=to_user_id)
            except User.DoesNotExist:
                raise Http404
            from_user = request.user
            from_user.relationships.add(to_user)

            response_data={'status':'success'}
            return HttpResponse(simplejson.dumps(response_data), mimetype='application/json')
    raise Http404


@csrf_exempt
def api_facebook_connect_by_token(request):
    ret = None
    if request.method == 'POST':
        form = FacebookConnectForm(request.POST)
        if form.is_valid():
            try:
                app = providers.registry.by_id(FacebookProvider.id)\
                .get_app(request)
                access_token = form.cleaned_data['access_token']
                token = SocialToken(app=app,
                    token=access_token)
                login = fb_complete_login(app, token)
                login.token = token
                login.state = SocialLogin.state_from_request(request)
                ret = complete_social_login(request, login)
            except:
                # FIXME: Catch only what is needed
                pass
    if not ret:
        raise Http404
    user_source = UserResource()
    bundle = user_source.build_bundle(obj=request.user, request=request)
    bundle = user_source.full_dehydrate(bundle)
    bundle = user_source.alter_detail_data_to_serialize(request, bundle)
    return user_source.create_response(request, bundle)


@csrf_exempt
def api_twitter_connect_by_token(request):
    ret = None
    if request.method == 'POST':
        try:
            adapter = TwitterOAuthAdapter()
            app = adapter.get_provider().get_app(request)
            access_token = request.POST.get('access_token')
            access_token_secret = request.POST.get('access_token_secret')
            token = SocialToken(app=app, token=access_token)
            login = twitter_complete_login(request, app, access_token, access_token_secret)

            login.token = token
            login.state = SocialLogin.state_from_request(request)
            ret = complete_social_login(request, login)
        except Exception as e:
            # FIXME: Catch only what is needed
            pass

    if not ret:
        raise Http404
    user_source = UserResource()
    bundle = user_source.build_bundle(obj=request.user, request=request)
    bundle = user_source.full_dehydrate(bundle)
    bundle = user_source.alter_detail_data_to_serialize(request, bundle)
    return user_source.create_response(request, bundle)


def twitter_complete_login(request, app, access_token, access_token_secret):
    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    user = simplejson.loads(get_twitter_user_info(url, app, access_token, access_token_secret))
    extra_data = user
    uid = extra_data['id']
    user = User(username=extra_data['screen_name'])
    account = SocialAccount(user=user,
        uid=uid,
        provider=TwitterProvider.id,
        extra_data=extra_data)
    return SocialLogin(account)


def get_twitter_user_info(url, app, access_token, access_token_secret):
    token = Token(access_token, access_token_secret)
    consumer = Consumer(app.key, app.secret)
    client = Client(consumer, token)
    method="GET"
    params=dict()
    headers=dict()
    body = urllib.urlencode(params)
    response, content = client.request(url, method=method, headers=headers, body=body)

    if response['status'] != '200':
        raise OAuthError('OAuth Error')

    return content