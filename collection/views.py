from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from .models import Collection
from utils import http, codes, messages


@http.json_response()
@http.requires_token()
@http.required_parameters(["collection_id"])
@csrf_exempt
def show_collection(request, user):
    """
        @apiDescription Информация о Пользователе. user_id is optional
        @api {get} /user/info/ 01. Информация о Пользователе
        @apiGroup 02. User
        @apiHeader {String} auth-token Токен авторизации
        @apiParam {integer} [user_id] User id
        @apiSuccess {json} result Json
    """
    try:
        new_collection = Collection.objects.get(
            pk=int(request.POST.get("collection_id") or request.GET.get("collection_id")))
    except:
    # except ObjectDoesNotExist:
    #     new_collection = None
        return http.code_response(code=codes.BAD_REQUEST, message=messages.COLLECTION_NOT_FOUND)
    return {
        "collection": new_collection.json(user=user),
    }
