from django.contrib.auth.backends import ModelBackend

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class PhoneModelBackend(ModelBackend):

    def authenticate(self, request, username=None, email=None, phone=None, password=None, **kwargs):
        if email:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return user
                else:
                    return None
            except:
                return None

        try:
            if phone and len(phone) >= 10:
                if User.objects.filter(phone__endswith=phone[-10:]).count() == 1:
                    user = User.objects.filter(phone__endswith=phone[-10:])[0]
                else:
                    user = User.objects.get(phone__iexact=username or phone)
            else:
                user = User.objects.get(phone__iexact=username or phone)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
