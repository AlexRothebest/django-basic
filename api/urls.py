from django.contrib import admin
from django.urls import path

from .views import login, logout, add_user, restore_password


urlpatterns = [
	path('login/', login),
	path('logout/', logout),
	path('add_user/', add_user),
	path('restore_password/', restore_password)
]