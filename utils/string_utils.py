import re
from django.core.validators import validate_email


def empty_to_none(s):
    """
    :param s: String to be converted.
    :return: If string is empty returns None; otherwise returns string itself.
    """
    if s is not None:
        if len(s) == 0:
            return None
    return s


def format_phone(phone):
    """
    Format phone
    """
    phone = re.sub("[^0-9]", "", phone)
    return "+" + phone


def valid_email(email):
    try:
        validate_email(email)
        return True
    except:
        return False


def valid_phone(phone):
    """
    Dummy check for phone validation.
    TODO: more smart validation required.
    """
    if phone is None:
        return False, None
    phone = re.sub("[^0-9]", "", phone)
    # if len(phone) >= 10 and len(phone) <= 13:
    if 10 <= len(phone) <= 13:
        return True, "+" + phone
    return False, None

