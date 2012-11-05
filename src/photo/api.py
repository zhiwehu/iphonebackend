from django.conf.urls import url
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import login

from relationships.models import Relationship, RelationshipStatus
from sorl.thumbnail import get_thumbnail
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.http import HttpForbidden, HttpUnauthorized
from tastypie.resources import ModelResource
from tastypie import fields

from models import Photo, Comment, Like, Profile
from tastypie.utils import trailing_slash
from utils import get_user_list

class ProfileResource(ModelResource):
    class Meta:
        queryset = Profile.objects.all()
        resource_name = 'profile'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()


class UserResource(ModelResource):
    followers = fields.ApiField(attribute='followers', null=True, blank=True, readonly=True)
    following = fields.ApiField(attribute='following', null=True, blank=True, readonly=True)
    friends = fields.ApiField(attribute='friends', null=True, blank=True, readonly=True)
    profile = fields.OneToOneField(ProfileResource, 'profile', null=True, blank=True, full=True, readonly=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        excludes = ['password', 'is_active', 'is_staff', 'is_superuser']
        filtering = {
            'email': ALL,
        }

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.raw_post_data,
            format=request.META.get('CONTENT_TYPE', 'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                }, HttpForbidden)
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
            }, HttpUnauthorized)

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False}, HttpUnauthorized)

    def dehydrate_followers(self, bundle):
        return get_user_list(bundle.obj.relationships.followers())

    def dehydrate_following(self, bundle):
        return get_user_list(bundle.obj.relationships.following())

    def dehydrate_friends(self, bundle):
        return get_user_list(bundle.obj.relationships.friends())


class PhotoResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    thumbnail = fields.ApiField(attribute='thumbnail', null=True, blank=True, readonly=True)

    class Meta:
        queryset = Photo.objects.all()
        resource_name = 'photo'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'created': ['exact', 'lt', 'lte', 'gte', 'gt'],
            'is_publish': ALL,
        }

    def dehydrate_thumbnail(self, bundle):
        if bundle.obj.file:
            im = get_thumbnail(bundle.obj.file, '100x100', crop='center', quality=99)
            return {
                'file_url': im.url
            }
        else:
            return {
                'file_url': None
            }


class CommentResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    photo = fields.ForeignKey(PhotoResource, 'photo')

    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'photo': ALL_WITH_RELATIONS,
            'created': ['exact', 'lt', 'lte', 'gte', 'gt'],
        }


class LikeResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    photo = fields.ForeignKey(PhotoResource, 'photo', full=True)

    class Meta:
        queryset = Like.objects.all()
        resource_name = 'like'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'photo': ALL_WITH_RELATIONS,
        }


class RelationshipStatusResource(ModelResource):
    class Meta:
        queryset = RelationshipStatus.objects.all()
        resource_name = 'relationshipstatus'


class RelationshipResource(ModelResource):
    from_user = fields.ToOneField(UserResource, 'from_user', full=True)
    to_user = fields.ToOneField(UserResource, 'to_user', full=True)
    status = fields.ToOneField(RelationshipStatusResource, 'status')

    class Meta:
        queryset = Relationship.objects.all()
        resource_name = 'relationship'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'from_user': ALL_WITH_RELATIONS,
            'to_user': ALL_WITH_RELATIONS,
        }