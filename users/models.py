# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe
from django.conf import settings
import os

# Create your models here.

class NewUser(models.Model):
	"""
	This class hold the information about the users Database of the system.
	This is essentially like a wrapper for the existing User model, with enhanced functionalities.

	User model (Default) contains basic info such as username,firstname,lastname,email etc...
	Additional info such as phone number, company name and position are capture here.
	"""
	user = models.OneToOneField(User, unique=True) 

	# Mobile no
        phone_regex = RegexValidator(regex=r'^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	phone = models.CharField(validators=[phone_regex], blank=True, max_length=20)

	company = models.CharField(max_length=64, blank=True)

	position = models.CharField(max_length=64, blank=True)

	#profile_pic = models.ImageField(upload_to=settings.MEDIA_ROOT, blank = True)
	profile_pic = models.ImageField(blank = True, null=True)

	# Default User Status Give in the User model are only Active and Inactive.\
	# In order to provided more flexibility this STATUS_CHOICES are user.
	STATUS_CHOICES = (
			('active', 'Active'),
			('inactive', 'Inctive'),
			('archived', 'Archived'),
			)

	user_status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')

	def image_tag(self):
		# used in the admin site model as a "thumbnail"
		if self.profile_pic:
			return mark_safe('<img src="%s" width="150" height="150" />'%(os.path.join('/',settings.MEDIA_URL, os.path.basename(str(self.profile_pic)))))
		else:
			return '%s, ID: %d' % (self.user.username, self.id)
		image_tag.short_description = 'Image'    

	
	def __unicode__(self):
                desc = '%s, ID: %d' % (self.user.username, self.id)
                return desc

class SearchStats(models.Model):
	"""
	Each User Stats
	"""
	date = models.DateField()

	users_added = models.PositiveIntegerField(default = 0, blank=True)

	api_usage = models.PositiveIntegerField(default = 0, blank=True)

	def __unicode__(self):
                desc = 'Date:%s, Users Added: %d, Api Usage:%d' % (self.date, self.users_added, self.api_usage)
                return desc

class SearchSummary(SearchStats):
	class Meta:
		proxy = True
		verbose_name = 'Search Summary'
		verbose_name_plural = 'Search Summary'

