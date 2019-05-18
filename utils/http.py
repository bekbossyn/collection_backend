from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from collection_backend import settings
from . import codes, messages, string_utils, token


def json_response():
    """
    Decorator that wraps response into json.
    """
    def decorator(func):

        @wraps(func)
        def inner(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
                if not ('code' in response):
                    response['code'] = codes.OK
            except ObjectDoesNotExist as e:
                response = code_response(code=codes.BAD_REQUEST,
                                         message=messages.NOT_FOUND,
                                         error=str(e))
            except Exception as e:
                # TODO: add logger
                response = code_response(codes.SERVER_ERROR, error=str(e))
            return JsonResponse(response)
        return inner
    return decorator


def code_response(code, message=None, error=None, field=None):
    result = {'code': code}
    if message:
        message = message.copy()
        result['message'] = message
        if field:
            for k, v in result['message'].items():
                result['message'][k] = v + " " + field
    if error:
        result['error'] = error
    return result


def required_parameters(parameters_list):
    """
    Decorator to make a view only accept request with required parameters.
    :param parameters_list: list of required parameters.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method == "POST":
                for parameter in parameters_list:
                    if len(parameter) >= 3 and parameter[-2:] == "[]":
                        list_parameter = parameter[:-2]
                    else:
                        list_parameter = parameter
                    value = string_utils.empty_to_none(request.POST.get(parameter) or request.FILES.get(parameter) or
                                                       request.POST.get(list_parameter) or request.FILES.get(
                        list_parameter))
                    if value is None:
                        return code_response(code=codes.BAD_REQUEST,
                                             message=messages.MISSING_REQUIRED_PARAMS,
                                             field=parameter)
            else:
                for parameter in parameters_list:
                    if len(parameter) >= 3 and parameter[-2:] == "[]":
                        list_parameter = parameter[:-2]
                    else:
                        list_parameter = parameter
                    value = string_utils.empty_to_none(
                        request.GET.get(list_parameter) or request.POST.get(list_parameter))
                    if value is None:
                        return code_response(code=codes.BAD_REQUEST,
                                             message=messages.MISSING_REQUIRED_PARAMS, field=list_parameter)

            return func(request, *args, **kwargs)
        return inner
    return decorator


def ok_response():
    return code_response(codes.OK)


def extract_token_from_request(request):
    """
    Extracts token string from request. First tries to get it from AUTH_TOKEN header,
    if not found (or empty) tries to get from cookie.
    :param request:
    :return: Token string found in header or cookie; null otherwise.
    """
    header_names_list = settings.AUTH_TOKEN_HEADER_NAME
    token_string = None
    for name in header_names_list:
        if name in request.META:
            token_string = string_utils.empty_to_none(request.META[name])

    if token_string is None:
        token_string = request.COOKIES.get(settings.AUTH_TOKEN_COOKIE_NAME, None)

    return string_utils.empty_to_none(token_string)


def requires_token(optional=False):
    """
    Decorator to make a view only accept request with valid token.
    if optional, user will be sent as None when there is no token.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            token_string = extract_token_from_request(request)
            if not optional and token_string is None:
                return code_response(code=codes.BAD_CREDENTIALS,
                                     message=messages.MISSING_TOKEN)

            user = token.verify_token(token_string)

            if not optional and user is None:
                return code_response(code=codes.BAD_CREDENTIALS,
                                     message=messages.INVALID_TOKEN)

            return func(request, user, *args, **kwargs)
        return inner
    return decorator


