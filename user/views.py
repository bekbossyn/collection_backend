from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from utils import http, codes, messages
from utils.constants import LANGUAGES, ON_SAVE, ON_FULL, ON_EGGS
from utils.upload import resize_image

User = get_user_model()


@http.json_response()
@http.requires_token()
# @http.required_parameters(["user_id"])
@csrf_exempt
def info(request, user):
    """
        @apiDescription Информация о Пользователе. user_id is optional
        @api {get} /user/info/ 01. Информация о Пользователе
        @apiGroup 02. User
        @apiHeader {String} auth-token Токен авторизации
        @apiParam {integer} [user_id] User id
        @apiSuccess {json} result Json
    """
    try:
        new_user = User.objects.get(pk=int(request.POST.get("user_id") or request.GET.get("user_id")))
    except:
    # except ObjectDoesNotExist:
        new_user = user
    #     return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_NOT_FOUND)
    return {
        "user": new_user.json(user=user),
    }


@http.json_response()
@http.requires_token()
@csrf_exempt
def update_profile(request, user):
    """
        @apiDescription Обновить профиль.
        @api {post} /user/update_profile/ 02. Обновить профиль
        @apiGroup 02. User
        @apiHeader {String} auth-token Токен авторизации
        @apiParam {String} [name] Name
        @apiParam {Integer} [language] Language {RUSSIAN = 1, KAZAKH = 2, ENGLISH = 3}
        @apiParam {Integer} [on_save] On Save {ON_SAVE_SUM_30 = 30, ON_SAVE_SUM_31 = 31}
        @apiParam {Integer} [on_full] On Full {ON_FULL_OPEN_FOUR = 1, ON_FULL_FINISH_GAME = 2}
        @apiParam {Boolean} [ace_allowed] Ace allowed {True, False}
        @apiParam {Integer} [on_eggs] On eggs {ON_EGGS_OPEN_FOUR = 1, ON_EGGS_OPEN_DOUBLE = 2}

        @apiSuccess {json} result Json
    """
    try:
        name = request.POST.get("name") or request.GET.get("name")
        if name:
            user.name = name
    except:
        pass
    try:
        language = int(request.POST.get("language") or request.GET.get("language"))
        if language not in [x[0] for x in LANGUAGES]:
            return http.code_response(code=codes.BAD_REQUEST, message=messages.INVALID_PARAMS, field="language")
        user.language = language
    except:
        pass
    #   user's GameSetting
    if user.rooms.filter(active=True).count() == 0:
        try:
            on_save = int(request.POST.get("on_save") or request.GET.get("on_save"))
            if on_save and on_save not in [x[0] for x in ON_SAVE]:
                return http.code_response(code=codes.BAD_REQUEST, message=messages.INVALID_PARAMS, field="on_save")
            user.game_setting.on_save = on_save
        except:
            pass
        try:
            on_full = int(request.POST.get("on_full") or request.GET.get("on_full"))
            if on_full and on_full not in [x[0] for x in ON_FULL]:
                return http.code_response(code=codes.BAD_REQUEST, message=messages.INVALID_PARAMS, field="on_full")
            user.game_setting.on_full = on_full
        except:
            pass
        try:
            ace_allowed = request.POST.get("ace_allowed") or request.GET.get("ace_allowed")
            if ace_allowed is not None and ace_allowed.lower() in ['true', 'false']:
                ace_allowed = ace_allowed.lower() == 'true'
                user.game_setting.ace_allowed = ace_allowed
        except:
            pass
        try:
            on_eggs = int(request.POST.get("on_eggs") or request.GET.get("on_eggs"))
            if on_eggs and on_eggs not in [x[0] for x in ON_EGGS]:
                return http.code_response(code=codes.BAD_REQUEST, message=messages.INVALID_PARAMS, field="on_eggs")
            user.game_setting.on_eggs = on_eggs
        except:
            pass
        user.game_setting.save()
    user.save()
    return {
        "user": user.json(user=user)
    }


@http.json_response()
@http.requires_token()
@http.required_parameters(["avatar"])
@csrf_exempt
def update_avatar(request, user):
    """
        @apiDescription Обновить аватар.
        @api {post} /user/update_avatar/ 03. Обновить аватар
        @apiGroup 02. User
        @apiHeader {String} auth-token Токен авторизации
        @apiParam {File} avatar Файл изображения
        @apiSuccess {json} result Json
    """
    user.avatar = request.FILES.get("avatar")
    user.avatar_big = request.FILES.get("avatar")
    user.save()
    resize_image(user.avatar, user.avatar_big)
    return {
        "user": user.json(user=user),
    }


@http.json_response()
@http.requires_token()
@csrf_exempt
def remove_avatar(request, user):
    """
        @apiDescription Удалить аватар.
        @api {post} /user/remove_avatar/ 04. Удалить аватар
        @apiGroup 02. User
        @apiHeader {String} auth-token Токен авторизации
        @apiSuccess {json} result Json
    """
    user.avatar = None
    user.avatar_big = None
    user.save()
    return {
        "user": user.json(user=user),
    }


@http.json_response()
@http.requires_token()
@csrf_exempt
def list_users(request, user):
    """
        @apiDescription Список всех пользователей.
        @api {post} /user/list_users/ 05. Список пользователей
        @apiGroup 02. User
        @apiHeader {String} auth-token Токен авторизации
        @apiSuccess {json} result Json
    """
    users = [new_user.json(user=user) for new_user in User.objects.all().exclude(is_admin=True)]
    return {
        "list": users,
    }

