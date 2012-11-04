from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

class Photo(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=255)
    #todo
    #Photo is a url field
    #Write a api to upload file and return this file's url
    file = models.ImageField(verbose_name=_(u'Photo File'), upload_to='photo')


class Like(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    photo = models.OneToOneField(Photo, verbose_name=_(u'Photo'))


class Comment(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    photo = models.ForeignKey(Photo, verbose_name=_(u'Photo'))
    content = models.CharField(verbose_name=_(u'Content'), max_length=140)


