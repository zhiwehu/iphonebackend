from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api

from photo.api import UserResource, PhotoResource, CommentResource, RelationshipResource

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(PhotoResource())
v1_api.register(CommentResource())
v1_api.register(RelationshipResource())

photo_resource = PhotoResource()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webapp.views.home', name='home'),
    # url(r'^webapp/', include('webapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/', include(v1_api.urls))


)
