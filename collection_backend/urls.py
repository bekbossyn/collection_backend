"""collection_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views
from .settings import api_name, api_version

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_name + api_version, views.test_collection, name='test_collection'),
    path(api_name + api_version + 'collection/', include('collection.urls', namespace='collection')),
    path(api_name + api_version + 'core/', include('core.urls', namespace='core')),
    path(api_name + api_version + 'user/', include('user.urls', namespace='user')),
]