from django.contrib.auth.models import User

from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie import fields

from models import Photo, Comment


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['password', 'is_active', 'is_staff', 'is_superuser']
        filtering = {
            'email': ALL,
            }


class PhotoResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = Photo.objects.all()
        resource_name = 'photo'
        authorization = Authorization()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'created': ['exact', 'lt', 'lte', 'gte', 'gt'],
            }


class CommentResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    photo = fields.ForeignKey(PhotoResource, 'photo')

    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        authorization = Authorization()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'photo': ALL_WITH_RELATIONS,
            'created': ['exact', 'lt', 'lte', 'gte', 'gt'],
            }