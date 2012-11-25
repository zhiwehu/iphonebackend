from django.conf.urls import url
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.urlresolvers import resolve
from django.db import IntegrityError

from relationships.models import Relationship, RelationshipStatus
from sorl.thumbnail import get_thumbnail
from tastypie.authentication import BasicAuthentication, Authentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest
from tastypie.http import HttpForbidden, HttpUnauthorized
from tastypie.models import ApiKey
from tastypie.resources import ModelResource
from tastypie import fields

from models import Photo, Comment, Like, Profile, Report, Message
from tastypie.utils import trailing_slash
from utils import get_user_list


class ReadonlyAuthentication(BasicAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
            return True
        else:
            return super(ReadonlyAuthentication, self).is_authenticated(request, **kwargs)


class OwnerAuthorization(DjangoAuthorization):
    def get_object(self, request):
        try:
            pk = resolve(request.path)[2]['pk']
        except IndexError, KeyError:
            object = None # or raise Exception('Wrong URI')
        else:
            try:
                object = self.resource_meta.object_class.objects.get(pk=pk)
            except self.resource_meta.DoesNotExist:
                object = None
        return object

    def is_authorized(self, request, object=None):
        if request.method == 'PUT' or request.method == 'PATCH':
            object = self.get_object(request)
            if object:
                try:
                    if object == request.user or object.user == request.user:
                        return True
                except:
                    pass
            return False
        else:
            return super(OwnerAuthorization, self).is_authorized(request, object)

    def read_detail(self, object_list, bundle):
        """
        Returns either ``True`` if the user is allowed to read the object in
        question or throw ``Unauthorized`` if they are not.
        Returns ``True`` by default.
        """
        return True


class ProfileResource(ModelResource):
    class Meta:
        allowed_methods = ['get', 'put']
        queryset = Profile.objects.all()
        resource_name = 'profile'
        authentication = ReadonlyAuthentication()
        authorization = OwnerAuthorization()


class CreateUserResource(ModelResource):
    profile = fields.OneToOneField(ProfileResource, 'profile', null=True, blank=True)

    class Meta:
        allowed_methods = ['post']
        object_class = User
        authentication = Authentication()
        authorization = Authorization()
        include_resource_uri = False
        fields = ['username', 'email', 'password']

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(CreateUserResource, self).obj_create(bundle, request, **kwargs)
            bundle.obj.set_password(bundle.data.get('password'))
            bundle.obj.save()

            birthday = bundle.data.get('birthday')
            gender = bundle.data.get('gender')
            avatar_url = bundle.data.get('avatar_url')
            Profile.objects.create(user=bundle.obj, birthday=birthday, gender=gender, avatar_url=avatar_url)

            return bundle
        except IntegrityError as e:
            raise BadRequest(e.message)


class UserResource(ModelResource):
    followers = fields.ApiField(attribute='followers', null=True, blank=True, readonly=True)
    following = fields.ApiField(attribute='following', null=True, blank=True, readonly=True)
    friends = fields.ApiField(attribute='friends', null=True, blank=True, readonly=True)
    apikey = fields.ApiField(attribute='apikey', null=True, blank=True, readonly=True)
    profile = fields.OneToOneField(ProfileResource, 'profile', null=True, blank=True, full=True, readonly=True)

    class Meta:
        allowed_methods = ['get', 'put']
        queryset = User.objects.all()
        resource_name = 'user'
        authentication = ReadonlyAuthentication()
        authorization = OwnerAuthorization()
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
                bundle = self.build_bundle(obj=user, request=request)
                bundle = self.full_dehydrate(bundle)
                bundle = self.alter_detail_data_to_serialize(request, bundle)
                return self.create_response(request, bundle)

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

    def dehydrate_apikey(self, bundle):
        try:
            apikey = ApiKey.objects.get(user=bundle.obj)
            return apikey.key
        except:
            pass
        return ''


class PhotoResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    thumbnail = fields.ApiField(attribute='thumbnail', null=True, blank=True, readonly=True)
    like_count = fields.IntegerField(attribute='like_count', default=0, readonly=True)
    comment_count = fields.IntegerField(attribute='comment_count', default=0, readonly=True)

    class Meta:
        queryset = Photo.objects.all().order_by('-created')
        resource_name = 'photo'
        authentication = ReadonlyAuthentication()
        authorization = OwnerAuthorization()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'created': ['exact', 'lt', 'lte', 'gte', 'gt'],
            'is_publish': ALL,
        }

    def dehydrate_like_count(self, bundle):
        like_count = Like.objects.filter(photo=bundle.obj).count()
        return like_count

    def dehydrate_comment_count(self, bundle):
        return bundle.obj.comment_set.count()

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
    user = fields.ForeignKey(UserResource, 'user', full=True)
    photo = fields.ForeignKey(PhotoResource, 'photo')

    class Meta:
        queryset = Comment.objects.all().order_by('-created')
        resource_name = 'comment'
        authentication = ReadonlyAuthentication()
        authorization = Authorization()
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
        authentication = ReadonlyAuthentication()
        authorization = Authorization()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'photo': ALL_WITH_RELATIONS,
        }


class RelationshipStatusResource(ModelResource):
    class Meta:
        queryset = RelationshipStatus.objects.all()
        resource_name = 'relationshipstatus'
        allowed_method = ['get']


class RelationshipResource(ModelResource):
    from_user = fields.ToOneField(UserResource, 'from_user', full=True)
    to_user = fields.ToOneField(UserResource, 'to_user', full=True)
    status = fields.ToOneField(RelationshipStatusResource, 'status')

    class Meta:
        queryset = Relationship.objects.all()
        resource_name = 'relationship'
        authentication = ReadonlyAuthentication()
        authorization = OwnerAuthorization()
        filtering = {
            'from_user': ALL_WITH_RELATIONS,
            'to_user': ALL_WITH_RELATIONS,
        }


class ReportResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', null=True, blank=True)
    photo = fields.ForeignKey(PhotoResource, 'photo')
    class Meta:
        resource_name = 'report'
        allowed_methods = ['post']
        object_class = Report
        authentication = Authentication()
        authorization = Authorization()


class MessageResource(ModelResource):
    from_user = fields.ForeignKey(UserResource, 'from_user', full=True, readonly=True)
    to_user = fields.ForeignKey(UserResource, 'to_user', full=True, readonly=True)
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'message'
        allowed_method = ['get', 'put']
        authentication = ReadonlyAuthentication()
        authorization = OwnerAuthorization()
        filtering = {
            'from_user': ALL_WITH_RELATIONS,
            'to_user': ALL_WITH_RELATIONS,
            }
