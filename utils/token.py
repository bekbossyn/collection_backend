from core.models import TokenLog

from django.conf import settings
from django.contrib.auth import get_user_model

import time
import jwt


User = get_user_model()


def create_token(user, remove_others=False):
    """
    Creates token string.
    :param remove_others: will remove all previous tokens of the user
    :param user: User for which token should be created.
    :return: authentication token.
    """

    #TODO Temporary, delete at production.
    # In order for a definite user to sign in from different devices.
    remove_others = False

    info = {
        'id': user.id,
        'timestamp': time.time()
    }
    token = jwt.encode(info, settings.JWT_KEY, settings.JWT_ALGORITHM).decode('utf-8')
    if remove_others:
        TokenLog.objects.filter(user=user, active=True).update(active=False)
    TokenLog.objects.create(user=user, token=token)
    return token


def verify_token(token_string):
    """
    Verifies token string.
    :param token_string: Token string to verify.
    :return: User object if token is valid; None is token is invalid.
    """
    try:
        result = jwt.decode(token_string, settings.JWT_KEY, settings.JWT_ALGORITHM)
        user_id = result['id']
        user = User.objects.get(id=user_id)
        user.tokens.get(token=token_string, active=True)
        if user.pk != user_id:
            return None
        return user
    except Exception as e:
        return None
