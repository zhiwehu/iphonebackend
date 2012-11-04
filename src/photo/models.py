from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

class Photo(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=255, null=True, blank=True)
    file = models.ImageField(verbose_name=_(u'Photo File'), upload_to='photo')
    is_publish = models.BooleanField(verbose_name=_(u'Is Publish'), default=False)


class Like(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    photo = models.OneToOneField(Photo, verbose_name=_(u'Photo'))


class Comment(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_(u'User'))
    photo = models.ForeignKey(Photo, verbose_name=_(u'Photo'))
    content = models.CharField(verbose_name=_(u'Content'), max_length=140)


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
    file = models.ImageField(verbose_name=_(u'Avatar File'), upload_to='avatar')