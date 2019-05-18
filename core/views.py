import datetime

from .models import Activation
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.views.decorators.csrf import csrf_exempt
from utils import http, codes, messages, token, oauth
from utils.string_utils import valid_phone, format_phone, valid_email


User = get_user_model()


@http.json_response()
@http.required_parameters(["username", "password"])
@csrf_exempt
def sign_in(request):
    """
        @apiDescription Вход с помощью номера телефона/почты/социальной сети и пароля.
        @apiGroup 01. Core
        @api {post} /core/sign_in/ 01. Вход в систему [sign_in]
        @apiName Sign in
        @apiDescription Авторизация через `email` или `номер телефона`
        @apiParam {String} username email or phone number
        @apiParam {String} password Password
        @apiSuccess {json} result Json
    """
    username = request.POST.get("username")
    password = request.POST.get("password")
    if valid_email(username):
        user = authenticate(request, email=username, password=password)
    else:
        phone = format_phone(username)
        user = authenticate(request, phone=phone, password=password)
    if user:
        #####################################################
        # save last login time. Hard code. Fix Later from core models.
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save()
        #####################################################
        return {
            'token': token.create_token(user, remove_others=True),
            'user': user.json(user=user)
        }
    return http.code_response(code=codes.BAD_REQUEST,
                              message=messages.WRONG_USERNAME_OR_PASSWORD)


def email_sign_up(email, password):
    if not valid_email(email):
        return None, http.code_response(code=codes.BAD_REQUEST,
                                        message=messages.INVALID_EMAIL)
    if User.objects.filter(email=email).exists():
        return None, http.code_response(code=codes.BAD_REQUEST,
                                        message=messages.EMAIL_ALREADY_EXISTS)
    Activation.objects.filter(
        email=email, to_reset=False,
        to_change_phone=False, to_change_email=False, used=False).update(used=True)
    activation = Activation.objects.create_email_signup_code(email, password)
    return activation, None


def phone_sign_up(phone, password):
    valid, phone = valid_phone(phone)
    if not valid:
        return None, http.code_response(code=codes.BAD_REQUEST,
                                        message=messages.WRONG_PHONE_FORMAT)
    if User.objects.filter(phone=phone).exists():
        return None, http.code_response(code=codes.BAD_REQUEST,
                                        message=messages.PHONE_ALREADY_EXISTS)
    Activation.objects.filter(
        phone=phone, to_reset=False,
        to_change_phone=False, to_change_email=False, used=False).update(used=True)
    activation = Activation.objects.create_phone_signup_code(phone=phone, password=password)
    return activation, None


#   DEPRECATED FOR NOW TODO add social login
def get_social_info(access_token, social_type):
    result = {
        'social_id': None,
        'full_name': '',
        'email': None,
        'phone': None,
        'avatar_url': None,
    }
    if social_type == 'facebook':
        info = oauth.get_facebook_info(access_token)
        if info:
            result['social_id'] = info['id']
            result['full_name'] = info.get('name', '')
            result['email'] = info.get('email')
            result['phone'] = info.get('phone') # not given
            result['avatar_url'] = settings.FACEBOOK_AVATAR_URL.format(info['id'])
            return result, None
    elif social_type == 'insta':
        info = oauth.get_instagram_info(access_token)
        if info and 'data' in info:
            result['social_id'] = info['data']['id']
            result['full_name'] = info['data'].get('full_name', '')
            result['email'] = info['data'].get('email') # not given
            result['phone'] = info['data'].get('phone') # not given
            result['avatar_url'] = info['data'].get('profile_picture')
            return result, None
    elif social_type == 'vk':
        info = oauth.get_vk_info(access_token)
        if info and not info.get('error'):
            response = info['response'][0]
            result['social_id'] = response['id']
            result['full_name'] = '{} {}'.format(response['first_name'],
                                                 response['last_name'])
            result['email'] = response.get('email') # not given
            result['phone'] = response.get('phone') # not given
            result['avatar_url'] = response.get('photo_200')
            return result, None
    elif social_type == 'google':
        info = oauth.get_google_info(access_token)
        if info:
            result['social_id'] = info['email']
            result['full_name'] = info.get('name') # not given
            result['email'] = info['email']
            result['phone'] = info.get('phone') # not given
            result['avatar_url'] = info.get('picture')
            return result, None
    return None, http.code_response(code=codes.BAD_REQUEST,
                                    message=messages.INVALID_SOCIAL_TOKEN)


@http.json_response()
@http.required_parameters(["name", "username", "password"])
@csrf_exempt
def sign_up(request):
    """
        @apiDescription Регистрация с помощью телефона или почты.
        <br>После регистрации, следует Завершение регистрации(`sign_up_complete`) с помощью высланного кода.<br>

        @api {post} /core/sign_up/ 02. Регистрация [sign_up]

        @apiName Sign Up

        @apiGroup 01. Core

        @apiParam {String} username E-mail or Phone
        @apiParam {String} name Name
        @apiParam {String} password Password

        @apiSuccess {json} result Json
    """
    username = request.POST.get("username")
    password = request.POST.get("password")
    sms = True

    if valid_email(username):
        #   Register via email
        activation, response = email_sign_up(username, password)
        if not activation:
            return response
        success_message = messages.EMAIL_HAS_BEEN_SENT
        sms = False
    else:
        #   Register via phone number
        activation, response = phone_sign_up(username, password)
        if not activation:
            return response
        success_message = messages.SMS_HAS_BEEN_SENT

    activation.name = request.POST.get('name')

    activation.save()
    if sms:
        activation.send_sms()
    else:
        activation.send_email()
    return http.code_response(code=codes.OK, message=success_message)


#   DEPRECATED FOR NOW.
@http.json_response()
@http.required_parameters(["name", "social_type", "access_token", "password", "country"])
@csrf_exempt
def social_sign_up(request):
    """
        @apiIgnore
        @apiDescription Регистрация с помощью социальной сети и (телефона или почты). Параметр rtype, для регистрации как риелтор.<br>
        1. делаете запрос на <code>facebook_login/vk_login/google_login/insta_login</code> в зависимости от соцсети<br>
        2.
            Если пользователь есть в системе, то придет <code>exists=true, user, token</code><br>
            Если пользователя нет в системе, то придет <code>exists=false, email, phone, full_name</code><br>
            Если phone или email есть, то подтверждение через код необязательно, т.к. доверяем соцсетям<br>
            Если мобилка, и <code>phone=null</code>, то необходимо заставить пользователя вбить номер телефона, и отправить <code>verify=phone</code><br>
            Если web, и <code>email=null</code>, то необходимо заставить пользователя вбить email, и отправить <code>verify=email</code><br>
            Если соцсеть выдала имейл либо телефон, то вы не сможете верифицировать другой имейл или телефон<br>
        3. При успешной регистрации без верификации (соцсеть отдала телефон и имейл), вернется token и user (метод social sign_up)<br>
        4. Если все таки верификация необходима, то нужно завершить регу через метод <code>sign_up_complete</code><br>

        @api {post} /core/sign_up/social/ 02. Регистрация через соцсети [social_sign_up]

        @apiGroup 01. Core

        @apiParam {String} name Name
        @apiParam {String} password Password
        @apiParam {String} country Country
        @apiParam {String} access_token Social access token
        @apiParam {String{facebook, google, insta, vk}} social_type
        @apiParam {String} [email] E-mail to verify
        @apiParam {String} [phone] Phone to verify
        @apiParam {Number{0-Владелец, 1-Частный Агент, 2-Агентство недвижимости, 3-Отель, 4-Хостел}} [rtype] Realtor Type
        @apiParam {Number} [commission] For Agencies(2) and Individuals(1) [from 0 to 100 in PERCENT]
        @apiParam {String} [person_id] Person Id(ИИН)
        @apiParam {String} [email] E-mail
        @apiParam {String} [address] Address
        @apiParam {String} [business_id] Business Id(БИН)
        @apiParam {String} [business_name] Business Name
        @apiParam {String} [contact_number] Contact Number if No <code>Phone</code>
        @apiParam {Files} [certificate_id] Certificate Ids generated. For all rtype except Owner<code>rtype=0</code>.
        @apiParam {String{email, phone}} [verify]

        @apiSuccess {json} result Json
    """
    social_type = request.POST.get("social_type")
    info, response = get_social_info(request.POST.get("access_token"),
                                     social_type)

    if not info:
        # invalid access token
        return response

    if info["email"] and User.objects.filter(email=info["email"]).exists():
        return http.code_response(code=codes.BAD_REQUEST,
                                  message=messages.EMAIL_ALREADY_EXISTS)

    if info["phone"] and User.objects.filter(phone=info["phone"]).exists():
        return http.code_response(code=codes.BAD_REQUEST,
                                  message=messages.PHONE_ALREADY_EXISTS)

    password = request.POST.get("password")
    if request.POST.get("verify") == "email":
        if not info["email"]:
            info["email"] = request.POST.get("email")
        activation, response = email_sign_up(info["email"], password)
        if not activation:
            return response
    elif request.POST.get("verify") == "phone":
        if not info["phone"]:
            info["phone"] = request.POST.get("phone")
        activation, response = phone_sign_up(info["phone"], password)
        if not activation:
            return response
    else:
        if not info["phone"] and not info["email"]:
            return http.code_response(code=codes.BAD_REQUEST,
                                      message=messages.PHONE_OR_EMAIL_REQUIRED)
        activation = Activation.objects.create_social_code(
            email=info["email"], phone=info["phone"], password=password)
    activation.set_social_id(social_type, info["social_id"])
    activation.email = activation.email or info["email"]
    activation.phone = activation.phone or info["phone"]
    activation.name = request.POST.get('name')
    activation.country = request.POST.get('country', '')

    if info["avatar_url"]:
        activation.handle_avatar(info["avatar_url"], save=False)

    activation.save()
    if request.POST.get("verify") == "phone":
        activation.send_sms()
        message = messages.SMS_HAS_BEEN_SENT
    elif request.POST.get("verify") == "email":
        activation.send_email()
        message = messages.EMAIL_HAS_BEEN_SENT
    else:
        if activation.phone:
            user, _ = User.objects.get_or_create(phone=activation.phone)
        else:
            user, _ = User.objects.get_or_create(email=activation.email)
        sign_up_user_complete(user, activation)
        return {
            "user": user.json(user=user),
            "token": token.create_token(user, remove_others=True)
        }
    return http.code_response(code=codes.OK, message=message)


def sign_up_user_complete(user, activation):
    """
    """
    for f in ["avatar", "name", "password", "phone", "email"]:
        # "fb_id", "insta_id", "vk_id",
        try:
            setattr(user, f, getattr(activation, f, None))
            user.save()
        except:
            # fb_id already exists
            pass
    activation.used = True
    activation.save()


@http.json_response()
@http.required_parameters(["username", "code"])
@csrf_exempt
def sign_up_complete(request):
    """
        @apiDescription Завершение регистрации. Полсе подтверждения высланного кода, регистрация считается завершенной, и только после
        этого пользователь числится в базе.

        @api {post} /core/sign_up_complete/ 03. Завершение регистрации [sign_up_complete]

        @apiName Sign Up Complete

        @apiGroup 01. Core

        @apiParam {String} username Registration phone or email
        @apiParam {String} code Code sent to phone or email

        @apiSuccess {json} result Json
    """
    username = request.POST.get("username")
    code = request.POST.get("code")
    if valid_email(username):
        if User.objects.filter(email=username).exists():
            # Check if user with such email already signed up.
            return http.code_response(code=codes.BAD_REQUEST,
                                      message=messages.USER_ALREADY_EXISTS)
        try:
            activation = Activation.objects.filter(email=username, to_reset=False, to_change_phone=False,
                                                   to_change_email=False, code=code, used=False)[0]
        except:
            return http.code_response(code=codes.BAD_REQUEST, message=messages.WRONG_ACTIVATION_KEY_OR_INVALID_EMAIL)
        u, _ = User.objects.get_or_create(email=activation.email)
    else:
        phone = format_phone(username)
        if User.objects.filter(phone=username).exists():
            # Check if user with such phone already signed up.
            return http.code_response(code=codes.BAD_REQUEST,
                                      message=messages.USER_ALREADY_EXISTS)
        try:
            activation = Activation.objects.filter(phone=phone, to_reset=False, to_change_phone=False,
                                                   to_change_email=False, code=code, used=False)[0]
        except:
            return http.code_response(code=codes.BAD_REQUEST, message=messages.WRONG_ACTIVATION_KEY_OR_INVALID_PHONE)
        u, _ = User.objects.get_or_create(phone=activation.phone)
    sign_up_user_complete(user=u, activation=activation)
    return {
        'token': token.create_token(u, remove_others=True),
        'user': u.json(user=u)
    }


@http.json_response()
@http.requires_token()
@http.required_parameters(["current_password", "new_password"])
@csrf_exempt
def change_password(request, user):
    """
        @apiDescription Изменение пароля
        @api {post} /core/change_password/ 04. Поменять пароль [change_password]
        @apiName Change password
        @apiGroup 01. Core
        @apiHeader {String} auth-token Токен авторизации
        @apiParam {String} current_password Current password
        @apiParam {String} new_password New password
        @apiSuccess {json} result Json
    """
    if user.check_password(request.POST.get("current_password")):
        user.set_password(request.POST.get("new_password"))
        user.save()
    else:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.WRONG_PASSWORD)
    return {
        "user": user.json(user=user)
    }


@http.json_response()
@http.requires_token()
@http.required_parameters(["new_phone"])
@csrf_exempt
def change_phone(request, user):
    """
        @apiDescription Изменение номера телефона
        <br>Завершение Изменения номера происходит в методе change_phone_complete
        @api {post} /core/change_phone/ 05. Поменять номер телефона [change_phone]
        @apiGroup 01. Core
        @apiHeader {String} auth-token Токен авторизации
        @apiParam {String} new_phone New Phone
        @apiSuccess {json} result Json
    """
    if User.objects.filter(phone=request.POST.get("new_phone")).exists():
        return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_ALREADY_EXISTS)
    valid, _ = valid_phone(request.POST.get("new_phone"))
    if not valid:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.WRONG_PHONE_FORMAT)
    Activation.objects.create_phone_change_code(phone=user.phone, email=user.email, new_phone=request.POST.get("new_phone"))
    return {
        "user": user.json(user=user)
    }


@http.json_response()
@http.requires_token()
@http.required_parameters(["new_phone", "code"])
@csrf_exempt
def change_phone_complete(request, user):
    """
        @apiDescription Завершение смены номера. Полсе подтверждения высланного кода, процесс считается завершенным.

        @api {post} /core/change_phone_complete/ 06. Завершение смены номера [change_phone_complete]

        @apiGroup 01. Core

        @apiHeader {String} auth-token Auth Token
        @apiParam {String} new_phone New phone or email
        @apiParam {String} code Code sent to phone or email

        @apiSuccess {json} result Json
    """
    try:
        activation = Activation.objects.filter(phone=user.phone,
                                               email=user.email,
                                               new_phone=request.POST.get("new_phone"),
                                               to_reset=False, to_change_phone=True,
                                               code=request.POST.get("code"), used=False)[0]
        if activation.phone != user.phone:
            raise Exception(messages.WRONG_ACTIVATION_KEY)
    except:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.WRONG_ACTIVATION_KEY_OR_INVALID_PHONE)
    if User.objects.filter(phone=activation.new_phone).exists():
        return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_ALREADY_EXISTS)
    u, _ = User.objects.get_or_create(phone=activation.phone, email=activation.email)
    u.phone = activation.new_phone
    u.save()

    activation.used = True
    activation.save()
    return {
        "user": u.json(user=user)
    }


@http.json_response()
@http.requires_token()
@http.required_parameters(["new_email"])
@csrf_exempt
def change_email(request, user):
    """
        @apiDescription Изменение номера телефона
        <br>Завершение Изменения почты происходит в методе change_email_complete
        @api {post} /core/change_email/ 07. Поменять почту [change_email]
        @apiGroup 01. Core
        @apiHeader {String} auth-token Токен авторизации
        @apiParam {String} new_email New email
        @apiSuccess {json} result Json
    """
    new_email = request.POST.get("new_email").lower()
    if User.objects.filter(email=new_email).exists():
        return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_ALREADY_EXISTS)
    if not valid_email(new_email):
        return http.code_response(code=codes.BAD_REQUEST, message=messages.INVALID_EMAIL)
    Activation.objects.create_email_change_code(email=user.email, phone=user.phone, new_email=new_email)
    return {
        "user": user.json(user=user)
    }


@http.json_response()
@http.requires_token()
@http.required_parameters(["new_email", "code"])
@csrf_exempt
def change_email_complete(request, user):
    """
        @apiDescription Завершение смены email. Полсе подтверждения высланного кода, процесс считается завершенным.

        @api {post} /core/change_email_complete/ 08. Завершение смены email [change_email_complete]

        @apiGroup 01. Core

        @apiHeader {String} auth-token Auth Token
        @apiParam {String} new_email New email
        @apiParam {String} code Code sent to phone or email

        @apiSuccess {json} result Json
    """
    new_email = request.POST.get("new_email").lower()
    try:
        activation = Activation.objects.filter(email=user.email,
                                               phone=user.phone,
                                               new_email=new_email,
                                               to_reset=False, to_change_email=True,
                                               code=request.POST.get("code"), used=False)[0]
        if activation.email != user.email:
            raise Exception(messages.INVALID_EMAIL)
    except:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.WRONG_ACTIVATION_KEY_OR_INVALID_EMAIL)
    if User.objects.filter(email=activation.new_email).exists():
        return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_ALREADY_EXISTS)
    u, _ = User.objects.get_or_create(email=activation.email, phone=activation.phone)
    u.email = activation.new_email
    u.save()

    activation.used = True
    activation.save()
    return {
        "user": u.json(user=user)
    }


@http.json_response()
@http.required_parameters(["phone", "new_password"])
@csrf_exempt
def reset_password(request):
    """
        @apiDescription Сброс пароля
        <br>Завершение Сброса пароля происходит в методе reset_password_complete

        @api {post} /core/reset_password/ 09. Сброс пароля [reset_password]
        @apiGroup 01. Core
        @apiParam {String} phone Phone
        @apiParam {String} new_password New Password
        @apiSuccess {json} result Json
    """
    phone = format_phone(request.POST.get("phone"))
    try:
        if len(phone) >= 10:
            if User.objects.filter(phone__endswith=phone[-10:]).count() == 1:
                user = User.objects.filter(phone__endswith=phone[-10:])[0]
            else:
                user = User.objects.get(phone__iexact=phone)
        else:
            user = User.objects.get(phone__iexact=phone)
    except:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_NOT_FOUND)
    Activation.objects.filter(phone=user.phone, to_reset=True, to_change_phone=False, to_change_email=False, used=False).update(used=True)
    Activation.objects.create_reset_code(phone=user.phone, new_password=request.POST.get("new_password"))
    return http.code_response(code=codes.OK, message=messages.SMS_HAS_BEEN_SENT)


@http.json_response()
@http.required_parameters(["phone", "code"])
@csrf_exempt
def reset_password_complete(request):
    """
        @apiDescription Завершение сброса пароля.
        <br>Полсе подтверждения высланного кода, процесс считается завершенным.

        @api {post} /core/reset_password_complete/ 10. Завершение сброса пароля [reset_password_complete]

        @apiGroup 01. Core

        @apiParam {String} phone Phone or email
        @apiParam {String} code Code sent to phone or email

        @apiSuccess {json} result Json
    """
    phone = format_phone(request.POST.get("phone"))

    try:
        if len(phone) >= 10:
            if User.objects.filter(phone__endswith=phone[-10:]).count() == 1:
                user = User.objects.filter(phone__endswith=phone[-10:])[0]
            else:
                user = User.objects.get(phone__iexact=phone)
        else:
            user = User.objects.get(phone__iexact=phone)
    except:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_NOT_FOUND)

    try:
        activation = Activation.objects.filter(phone=user.phone, to_reset=True, to_change_phone=False, code=request.POST.get("code"), used=False)[0]
    except:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.WRONG_ACTIVATION_KEY)

    user.password = activation.password
    user.save()

    activation.used = True
    activation.save()

    return {
        'token': token.create_token(user, remove_others=True),
        'user': user.json(user=user)
    }


@http.json_response()
@http.required_parameters(["email", "new_password"])
@csrf_exempt
def reset_email_password(request):
    """
        @apiDescription Cброс пароля по почте
        <br>Завершение Сброса пароля происходит в методе reset_email_password_complete

        @api {post} /core/reset_email_password/ 11. Cброс пароля по почте  [reset_email_password]

        @apiGroup 01. Core

        @apiParam {String} email Email
        @apiParam {String} new_password New Password

        @apiSuccess {json} result Json
    """
    if not User.objects.filter(email__iexact=request.POST.get("email")).exists():
        return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_NOT_FOUND)
    Activation.objects.filter(email=request.POST.get("email"), to_reset=True, to_change_phone=False,
                              to_change_email=False, used=False).update(used=True)
    activation = Activation.objects.create_email_reset_code(email=request.POST.get("email"), new_password=request.POST.get("new_password"))
    activation.send_reset_email()
    return http.code_response(code=codes.OK, message=messages.EMAIL_HAS_BEEN_SENT)


@http.json_response()
@http.required_parameters(["email", "code"])
@csrf_exempt
def reset_email_password_complete(request):
    """
        @apiDescription Завершение cброса пароля по почте

        @api {post} /core/reset_email_password_complete/ 12. Завершение cброса пароля по почте [reset_email_password_complete]

        @apiGroup 01. Core

        @apiParam {String} email Email
        @apiParam {String} code code

        @apiSuccess {json} result Json
    """
    if not User.objects.filter(email__iexact=request.POST.get("email")).exists():
        return http.code_response(code=codes.BAD_REQUEST, message=messages.USER_NOT_FOUND)
    try:
        activation = Activation.objects.filter(email__iexact=request.POST.get("email"),
                                               to_reset=True,
                                               code=request.POST.get("code"),
                                               used=False)[0]
    except:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.WRONG_ACTIVATION_KEY)
    u, _ = User.objects.get_or_create(email__iexact=activation.email)
    u.password = activation.password
    u.save()

    activation.used = True
    activation.save()

    return {
        'token': token.create_token(u, remove_others=True),
        'user': u.json(user=u)
    }


def social_authenticate(social_type, social_id, email=None, phone=None, full_name=""):
    user = None
    if social_type == "facebook":
        try:
            user = User.objects.get(fb_id=social_id)
        except:
            pass
    elif social_type == "insta":
        try:
            user = User.objects.get(insta_id=social_id)
        except:
            pass
    elif social_type == "vk":
        try:
            user = User.objects.get(vk_id=social_id)
        except:
            pass
    if not user:
        if email:
            try:
                user = User.objects.get(email=email)
                user.set_social_id(social_type, social_id)
            except:
                # User with email doesnt exist
                pass
        if phone:
            try:
                user = User.objects.get(phone=phone)
                user.set_social_id(social_type, social_id)
            except:
                # User with phone doesnt exist
                pass
    if user:
        return {
            'exists': True,
            'token': token.create_token(user, remove_others=True),
            'user': user.json(user=user)
        }
    return{
        'exists': False,
        'email': email,
        'full_name': full_name,
        'phone': phone
    }


#   DEPRECATED FOR NOW
@http.json_response()
@http.required_parameters(["access_token"])
def facebook_login(request):
    """
        @apiIgnore
        @apiDescription Вход с помощью аккаунта Фэйсбук
        <br>С помощью <code>access_token</code> выполняется аутентификация пользователя
        @api {post} /core/facebook_login/ 16. Вход с Фэйсбука [facebook_login]
        @apiName facebook_login
        @apiGroup 01. Core
        @apiParam {String} access_token Access token of facebook user.
        @apiSuccess {json} result Json representation of user with token.
    """
    access_token = request.POST.get('access_token')
    info = oauth.get_facebook_info(access_token)

    if info is None:
        return http.code_response(code=codes.BAD_REQUEST,
                                  message=messages.INVALID_FB_TOKEN)
    if 'id' not in info:
        return http.code_response(code=codes.BAD_REQUEST,
                                  message=messages.INVALID_FB_TOKEN)

    full_name = info.get('name', None)
    email = info.get('email', None)
    phone = info.get('phone', None)
    fb_id = info['id']
    return social_authenticate("facebook", fb_id, email, phone, full_name)


#   DEPRECATED FOR NOW
@http.json_response()
@http.required_parameters(["access_token"])
def insta_login(request):
    """
        @apiIgnore
        @apiDescription Вход с помошью аккаунта Инстаграм
        <br>С помощью <code>access_token</code> выполняется аутентификация пользователя
        @api {post} /core/insta_login/ 18. Вход с Инстаграма [insta_login]
        @apiName insta_login
        @apiGroup 01. Core
        @apiParam {String} access_token Access token of Instagram user.
        @apiSuccess {json} result Json representation of user with token.
    """
    access_token = request.POST.get('access_token')
    info = oauth.get_instagram_info(access_token)

    if info is None:
        return http.code_response(code=codes.BAD_REQUEST,
                                  message=messages.INVALID_INSTA_TOKEN)
    if 'data' not in info:
        return http.code_response(code=codes.BAD_REQUEST,
                                  message=messages.INVALID_INSTA_TOKEN)

    full_name = info['data'].get('full_name', None)
    insta_id = info['data']['id']
    email = info['data'].get('email')
    phone = info['data'].get('phone')
    return social_authenticate("insta", insta_id, email, phone, full_name)


#   DEPRECATED FOR NOW
@http.json_response()
@http.required_parameters(["access_token"])
def google_login(request):
    """
        @apiIgnore
        @apiDescription Вход с помощью Гугл Аккаунта
        <br>С помощью <code>access_token</code> выполняется аутентификация пользователя
        @api {post} /core/google_login/ 17. Вход с Гугл Аккаунта [google_login]
        @apiName google_login
        @apiGroup 01. Core
        @apiParam {String} access_token Access token of Google user.
        @apiSuccess {json} result Json representation of user with token.
    """
    access_token = request.POST.get('access_token')
    info = oauth.get_google_info(access_token)

    if info is None:
        return http.code_response(code=codes.BAD_REQUEST,
                                  message=messages.INVALID_GOOGLE_TOKEN)
    email = info.get('email')
    phone = info.get('phone')
    full_name = info.get('name')
    google_id = info.get('id')
    return social_authenticate("google", google_id, email, phone, full_name)


#   DEPRECATED FOR NOW
@http.json_response()
@http.required_parameters(["access_token"])
def vk_login(request):
    """
        @apiIgnore
        @apiDescription Вход с помощью Аккаунта VK
        <br>С помощью <code>access_token</code> выполняется аутентификация пользователя
        @api {post} /core/vk_login/ 19. Вход с ВК [vk_login]
        @apiName vk_login
        @apiGroup 01. Core
        @apiParam {String} access_token Access token of vk user.
        @apiSuccess {json} result Json representation of user with generated token.
    """
    access_token = request.POST.get('access_token')
    info = oauth.get_vk_info(access_token)

    if info is None or 'error' in info:
        return http.code_response(code=codes.BAD_REQUEST,
                                  message=messages.INVALID_VK_TOKEN,
                                  error=info['error'])
    info = info['response'][0]
    vk_id = info['id']
    full_name = '{} {}'.format(info.get('first_name', ""), info.get('last_name', ''))
    email = info.get('email')
    phone = info.get('phone')
    return social_authenticate("vk", vk_id, email, phone, full_name)


numbers = []
for x in range(0, 10):
    numbers.append(str(x))

doubles = numbers
doubles.append(".")

kazakh_doubles = numbers
kazakh_doubles.append(",")
kazakh_doubles.append(".")


def previous_date_fn(year, month, day):

    year_int = int(year)
    month_int = int(month)
    day_int = int(day)

    today = datetime.date(year_int, month_int, day_int)

    yesterday = today - datetime.timedelta(days=1)

    day = str(yesterday.day)

    if len(day) < 2:
        day = '0' + day
    month = str(yesterday.month)
    if len(month) < 2:
        month = '0' + month
    year = str(yesterday.year)
    return year, month, day
