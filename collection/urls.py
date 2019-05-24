from django.conf.urls import url

from . import views

app_name = "collection"

urlpatterns = [
    url(r'^show_collection/$', views.show_collection, name='show_collection'),
    # url(r'^update_profile/$', views.update_profile, name='update_profile'),
    # url(r'^update_avatar/$', views.update_avatar, name='update_avatar'),
    # url(r'^remove_avatar/$', views.remove_avatar, name='remove_avatar'),
    # url(r'^list_users/$', views.list_users, name='list_users'),
]
