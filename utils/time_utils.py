import time
import pytz

from django.conf import settings
from django.utils import timezone
from datetime import datetime


def dt_to_timestamp(dt):
    """
    Converts datetime object to unix timestamp
    """
    try:
        if dt:
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=pytz.utc)
            return int(time.mktime((timezone.localtime(dt)).timetuple()))
    except:
        return None


def timestamp_to_dt(timestamp):
    """
    Converts unix timestamp object to datetime
    """
    try:
        tz = pytz.timezone(settings.TIME_ZONE)
        return datetime.fromtimestamp(int(timestamp), tz)
    except:
        return None
