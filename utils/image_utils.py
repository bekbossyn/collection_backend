from django.conf import settings
from urllib.parse import urljoin


def get_url(image=None, path=None):
    if image:
        return urljoin(settings.SITE_URL, image.url)
    elif path:
        return urljoin(settings.SITE_URL, path)
    return None
