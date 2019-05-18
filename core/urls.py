from django.conf.urls import url

from . import views

app_name = "core"

urlpatterns = [

    url(r'^sign_in/$', views.sign_in, name='sign_in'),

    url(r'^sign_up/$', views.sign_up, name='sign_up'),
    url(r'^sign_up_complete/$', views.sign_up_complete, name='sign_up_complete'),

    # url(r'^sign_up/social/$', views.social_signup, name='social_signup'),

    url(r'^change_password/$', views.change_password, name='change_password'),

    url(r'^change_phone/$', views.change_phone, name='change_phone'),
    url(r'^change_phone_complete/$', views.change_phone_complete, name='change_phone_complete'),

    url(r'^change_email/$', views.change_email, name='change_email'),
    url(r'^change_email_complete/$', views.change_email_complete, name='change_email_complete'),

    url(r'^reset_password/$', views.reset_password, name='reset_password'),
    url(r'^reset_password_complete/$', views.reset_password_complete, name='reset_password_complete'),

    url(r'^reset_email_password/$', views.reset_email_password, name='reset_email_password'),
    url(r'^reset_email_password_complete/$', views.reset_email_password_complete, name='reset_email_password_complete'),

    # url(r'^facebook_login/$', views.facebook_login, name='facebook_login'),
    # url(r'^insta_login/$', views.insta_login, name='insta_login'),
    # url(r'^google_login/$', views.google_login, name='google_login'),
    # url(r'^vk_login/$', views.vk_login, name='vk_login'),

]


