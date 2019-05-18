import requests

from django.conf import settings
from io import BytesIO


def get_facebook_info(access_token):
    try:
        request_url = settings.FACEBOOK_INFO_URL.format(access_token)
        response = requests.get(request_url)
        if response.status_code == 200:
            return response.json()
    except:
        return None


def get_facebook_avatar(fb_id):
    try:
        fb_avatar_url = settings.FACEBOOK_AVATAR_URL.format(fb_id)
        response = requests.get(fb_avatar_url)
        if response.status_code == 200:
            fb_avatar_name = response.url.split('/')[-1]
            # fp = BytesIO()
            # fp.write(response.content)
            return fb_avatar_name, response.content
    except:
        pass
    return None, None


def get_instagram_info(access_token):
    try:
        request_url = settings.INSTAGRAM_INFO_URL.format(access_token)
        response = requests.get(request_url)
        if response.status_code == 200:
            return response.json()
    except:
        return None


def get_google_info(access_token):
    try:
        headers = {'Authorization': 'Bearer {0}'.format(access_token)}
        response = requests.get(settings.GOOGLE_INFO_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        return None


def get_vk_info(access_token):
    try:
        response = requests.get(settings.VK_INFO_URL.format(access_token))
        if response.status_code == 200:
            return response.json()
    except:
        return None
