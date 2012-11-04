from django.contrib import admin

from models import Photo, Comment, Like, Profile, Avatar

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

admin.site.register(Photo, PhotoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Avatar, AvatarAdmin)