from django.contrib import admin

from models import Photo, Comment, Like, Profile, Avatar, Report

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'file', 'user', 'is_publish', 'created')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'photo', 'content', 'created')

class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo', 'created')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'birthday', 'gender')

class AvatarAdmin(admin.ModelAdmin):
    list_display = ('id', 'file')

class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo_url', 'description', 'created')
    def photo_url(self, obj):
        if obj.photo:
            return u'<a href="%s" target="_blank">%s</a>' % (obj.photo.file.url, obj.photo)
        else:
            return ''
    photo_url.allow_tags = True

admin.site.register(Photo, PhotoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Avatar, AvatarAdmin)
admin.site.register(Report, ReportAdmin)