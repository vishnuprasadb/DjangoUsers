# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
import json

from .models import *


class BaseClass(object):

	def _return_json_error(self, errString, jsonify = True, status_code = 200):
		resp = {}
		resp["status"] = "error"
		resp["message"] = errString
		if jsonify:
			return JsonResponse(resp, status = status_code)
		else:
			return resp

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
                try:
                        response = super(BaseClass, self).dispatch(request, *args, **kwargs)
                except Exception as e:
			return self._return_json_error("Something went wrong. Please retry later.", True, 500)
		return response

        def http_method_not_allowed(self,request, *args, **kwargs):
                """
                This method will be called when the request Method is not found for that URL.
                """
		return self._return_json_error("Invalid HTTP Method", True, 405)

	def update_stats(self, user_count = False, api_count = False):
		
		try:
			daily_stat, ignore = SearchStats.objects.get_or_create(date = datetime.now().date())
		except Exception as e:
			print e
		stat_dirty = False

		if user_count:
			daily_stat.users_added += 1
			stat_dirty = True
		if api_count:
			daily_stat.api_usage += 1
			stat_dirty = True

		if stat_dirty:
			daily_stat.save()
		
class CreateUser(BaseClass, View):
	"""
	API to create an user.
	API: '/user/create/'
	Method(s): POST
	"""
	def post(self, request, *value_tuple, **value_dict):
		"""
		Request Body: {"username":<username>, "password": <password>, "email":<email>, "first_name":<first_name>, \
			       "last_name": <last_name>, "phone":<phone>, "company":<companyname>, "position": <position>}
		"""
		try:
                        data = json.loads(request.body.decode("utf-8"))
                except:
                        return self._return_json_error("Empty JSON", True, 400)

		username = data.get('username', None)
		password = data.get('password', None)
		email = data.get('email', None)
		first_name = data.get('first_name', None)
		last_name = data.get('last_name', None)
		phone = data.get('phone', None)
		company = data.get('company', None)
		position = data.get('position', None)

		if not (username or password or first_name or last_name or email):
                        return self._return_json_error("Please provide the following username, email, first_name, last_name to create an user.", True, 400)

		# Except the password every field is replaced by new set of data for User and NewUser
		user, created = User.objects.get_or_create(username = username)
		if created:
			user.set_password(password)
			self.update_stats(user_count=True) # Only if its a new user count in the stats
		user.email = email
		user.first_name = first_name
		user.last_name = last_name
		user.save()

		newuser, ignore = NewUser.objects.get_or_create(user = user)
		newuser.phone = phone
		newuser.company = company
		newuser.position = position
		newuser.save()

		success_resp = {}
		success_resp['status'] = 'success'
		success_resp['message'] = 'Created new user %s'%username if created else "User details updated for %s(except passwrod)"%username
		return JsonResponse(success_resp)

class Login(BaseClass, View):
	"""
	Login API: 
	API: '/login/'
	Method(s): POST
	"""
	def post(self, request, *value_tuple, **value_dict):
		"""Request Body: {"username":<username>, "password":<password>}"""
		try:
                        data = json.loads(request.body.decode("utf-8"))
                except:
                        return self._return_json_error("Empty JSON", True, 400)

		username = data.get('username', None)
		password = data.get('password', None)
		
		if not (username or password):
			errStr = 'Please provide username and password for authentication'
			return self._return_json_error(errStr, True, 401)

		try:
			user = User.objects.get(username = username)
		except:
			errStr = 'Invalid Username'
                        return self._return_json_error(errStr, True, 401)
		
                authenticated_user = authenticate(username=user.username, password=password)
                if authenticated_user is not None:
                        login(request, authenticated_user)
			success_resp = {}
			success_resp['status'] = 'success'
			success_resp['message'] = 'User is Logged in. Username:%s'%user.username
                        return JsonResponse(success_resp)
		else:
			errStr = 'Bad Credentials!'
                        return self._return_json_error(errStr, True, 401)

class Search(BaseClass, View):
	"""
	This API is used to search about user database in the system.
	API: 'user/search/'
	METHOD(s): GET
	"""
	@method_decorator(login_required)
	def get(self, request, *value_tuple, **value_dict):
		"""
		GET Request Params: 
			Sl.No	Name	Values
			1.	status  active,inactive,archived 
			2.	company	<company_name>
		"""
		self.status = request.GET.get('status', 'false')
		self.company = request.GET.get('company', 'false')

		self.update_stats(api_count=True)

		if self.status.lower() == 'false' and self.company.lower() == 'false':
			self.all_users = NewUser.objects.all()
			if self.all_users.exists():
				self.build_success_resp()
				return JsonResponse(self.success_resp)
			else:
				errStr = 'Looks like the database is Empty!'
				return self._return_json_error(errStr, True, 404)
		elif self.status.lower() != 'false' and self.company.lower() != 'false':
			if self.is_valid_user_status():
				self.all_users = NewUser.objects.filter(user_status = self.status.lower(), company__icontains = self.company)
			else:
				self.all_users = NewUser.objects.filter(company__icontains= self.company)
			if self.all_users.exists():
				self.build_success_resp()
				return JsonResponse(self.success_resp)
			else:
				errStr = 'Matching users NOT FOUND for company:%s, status: %s'%(self.company, self.status)
				return self._return_json_error(errStr, True, 404)
			
		elif self.status != 'false':
			if self.is_valid_user_status():
				self.all_users = NewUser.objects.filter(user_status = self.status.lower())
				if self.all_users.exists():
					self.build_success_resp()
					return JsonResponse(self.success_resp)
				else:
					print "Hey"
					errStr = 'Users with status "%s" NOT FOUND'%self.status
					return self._return_json_error(errStr, True, 404)
			else:
				errStr = 'Bad Request: Invalid User Status. Valid choices are (active,inactive,archived)'
				return self._return_json_error(errStr, True, 400)
		elif self.company != 'false':
			self.all_users = NewUser.objects.filter(company__icontains= self.company)
			if self.all_users.exists():
				self.build_success_resp()
				return JsonResponse(self.success_resp)
			else:
				errStr = 'Matching users NOT FOUND for company:%s'%self.company
				return self._return_json_error(errStr, True, 404)
		else:
			errStr = 'Something Went Wrong. Please try again'
			return self._return_json_error(errStr, True, 500)
			
	def build_success_resp(self):
		self.success_resp = {}
		self.success_resp['users'] = []
		self.success_resp['count'] = self.all_users.count()
		for user in self.all_users:
			_dict = {}
			user_attrs = ['username', 'email', 'first_name', 'last_name']
			for attr in user_attrs:
				_dict[attr] = getattr(user.user, attr)

			new_user_attrs = ['phone', 'company', 'position', 'user_status']
			for attr in new_user_attrs:
				_dict[attr] = getattr(user, attr)
			self.success_resp['users'].append(_dict)

	def is_valid_user_status(self):
		valid_user_statuses = ['active','inactive','archived']
		if self.status.lower() in valid_user_statuses:
			return True
		return False

class Logout(BaseClass, View):
        def get(self, request, *value_tuple, **value_dict):
		user = request.user
                logout(request)
   		success_resp = {}
                success_resp['status'] = 'success'
                success_resp['message'] = 'Successfully Logged out user:%s'%user
                return JsonResponse(success_resp)
