from django.conf import settings
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api

from photo.api import UserResource, PhotoResource, CommentResource, LikeResource, RelationshipResource, RelationshipStatusResource, ProfileResource, CreateUserResource, ReportResource

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(PhotoResource())
v1_api.register(CommentResource())
v1_api.register(LikeResource())
v1_api.register(RelationshipResource())
v1_api.register(RelationshipStatusResource())
v1_api.register(ProfileResource())
v1_api.register(CreateUserResource())
v1_api.register(ReportResource())

photo_resource = PhotoResource()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'photo.views.home', name='home'),
    # url(r'^webapp/', include('webapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/v1/photo/upload/$', 'photo.views.api_upload_photo', name='api_upload_photo'),
    url(r'^api/v1/avatar/upload/$', 'photo.views.api_upload_avatar', name='api_upload_avatar'),
    url(r'^api/v1/user/unfollow/$', 'photo.views.api_user_unfollow', name='api_user_unfollow'),
    url(r'^api/v1/user/follow/$', 'photo.views.api_user_follow', name='api_user_follow'),

    url(r'^api/', include(v1_api.urls))


)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^site_media/media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
    )

