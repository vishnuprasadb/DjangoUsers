from django.conf.urls import  url

from users.views import *

urlpatterns = (
        url(r'^search/$', Search.as_view(), name='search'),
        url(r'^create/$', CreateUser.as_view(), name='createuser'),
	)
