# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function
from builtins import (
         bytes, dict, int, list, object, range, str,
         ascii, chr, hex, input, next, oct, open,
         pow, round, super,
         filter, map, zip)

from django.contrib import admin
from django.db.models import Sum
from .models import *

class NewUserAdmin(admin.ModelAdmin):
        search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone', 'user__date_joined']
	fields = ('user', 'phone', 'company', 'position', 'image_tag', 'profile_pic', 'user_status',)
	list_display = ('image_tag',)
	readonly_fields = ('image_tag',)
	list_filter = ('user_status', 'company')

admin.site.register(NewUser, NewUserAdmin)

class StatsAdmin(admin.ModelAdmin):
        search_fields = ['date']
admin.site.register(SearchStats, StatsAdmin)

@admin.register(SearchSummary)
class StatsAdmin(admin.ModelAdmin):
	change_list_template = 'admin/search_stats.html'
        date_hierarchy = 'date'
	def changelist_view(self, request, extra_context=None):
		response = super().changelist_view(
		    request,
		    extra_context=extra_context,
		)
		try:
		    qs = response.context_data['cl'].queryset
		except (AttributeError, KeyError):
		    return response
		
		metrics = {
		    'total_users': Sum('users_added'),
		    'total_searches': Sum('api_usage'),
		}
		response.context_data['summary'] = list(
		    qs
		    .values('date')
		    .annotate(**metrics)
		    .order_by('-date')
		)
	
		response.context_data['summary_total'] = dict(
		qs.aggregate(**metrics)
		)
		
		return response
