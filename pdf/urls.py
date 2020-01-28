from django.contrib import admin
from django.urls import path, include

import main.urls, api.urls


urlpatterns = [
    path('', include('main.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]