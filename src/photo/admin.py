from django.contrib import admin

from models import Photo, Comment, Like

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'file', 'user', 'created')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'photo', 'content', 'created')

class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo', 'created')

admin.site.register(Photo, PhotoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)