from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from uuid import uuid4
import os
def get_random_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid4()), ext)
    return os.path.join('photo/', filename)

def get_random_avatar_filename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid4()), ext)
    return os.path.join('avatar/', filename)


class Photo(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=255, null=True, blank=True)
    file = models.ImageField(verbose_name=_(u'Photo File'), upload_to=get_random_filename)
    is_publish = models.BooleanField(verbose_name=_(u'Is Publish'), default=False)

    def __unicode__(self):
        return '%s: %s' % (self.title, self.file.name)


class Like(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    photo = models.ForeignKey(Photo, verbose_name=_(u'Photo'))


class Comment(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    photo = models.ForeignKey(Photo, verbose_name=_(u'Photo'))
    content = models.CharField(verbose_name=_(u'Content'), max_length=140)

    def __unicode__(self):
        return self.content


class Profile(models.Model):
    GENDER_CHOICE = (
        ('F', _(u'Female')),
        ('M', _(u'Male')),
    )
    user = models.OneToOneField(User, verbose_name=_(u'User'))
    birthday = models.DateField(verbose_name=_(u'Birthday'), null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True, verbose_name=_(u'Gender'), choices=GENDER_CHOICE)
    avatar_url = models.URLField(verbose_name=_(u'Avatar URL'), blank=True, null=True)


class Avatar(TimeStampedModel):
    file = models.ImageField(verbose_name=_(u'Avatar File'), upload_to=get_random_avatar_filename)


class Report(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'), null=True, blank=True)
    photo = models.ForeignKey(Photo, verbose_name=_(u'Photo'))
    description = models.TextField(verbose_name=_(u'Description'), max_length=1024)


class Message(TimeStampedModel):
    from_user = models.ForeignKey(User, verbose_name=_(u'From User'), related_name='message_from_user')
    to_user = models.ForeignKey(User, verbose_name=_(u'To User'), related_name='message_to_user')
    is_read = models.BooleanField(verbose_name=_(u'Is Read?'), default=False)
    description = models.TextField(verbose_name=_(u'Description'), max_length=1024)