from django.contrib.auth.models import User

from relationships.models import Relationship, RelationshipStatus
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie import fields

from models import Photo, Comment, Like
from utils import get_user_list


class UserResource(ModelResource):
    followers = fields.ApiField(attribute='followers', null=True, blank=True, readonly=True)
    following = fields.ApiField(attribute='following', null=True, blank=True, readonly=True)
    friends = fields.ApiField(attribute='friends', null=True, blank=True, readonly=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        excludes = ['password', 'is_active', 'is_staff', 'is_superuser']
        filtering = {
            'email': ALL,
        }

    def dehydrate_followers(self, bundle):
        return get_user_list(bundle.obj.relationships.followers())

    def dehydrate_following(self, bundle):
        return get_user_list(bundle.obj.relationships.following())

    def dehydrate_friends(self, bundle):
        return get_user_list(bundle.obj.relationships.friends())


class PhotoResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = Photo.objects.all()
        resource_name = 'photo'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
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
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'photo': ALL_WITH_RELATIONS,
            'created': ['exact', 'lt', 'lte', 'gte', 'gt'],
        }


class LikeResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    photo = fields.ForeignKey(PhotoResource, 'photo')

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
    from_user = fields.ToOneField(UserResource, 'from_user')
    to_user = fields.ToOneField(UserResource, 'to_user')
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