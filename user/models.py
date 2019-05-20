from django.db import models

from collection_backend import settings
from utils.constants import ON_SAVE, ON_SAVE_SUM_30, ON_FULL_OPEN_FOUR, ON_FULL, ON_EGGS, ON_EGGS_OPEN_FOUR
from utils.time_utils import dt_to_timestamp
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from utils.constants import HIDE_LAST, LANGUAGES, RUSSIAN
from utils.image_utils import get_url

from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.upload import avatar_upload


class MainUserManager(BaseUserManager):
    """
    Custom user manager.
    """

    def create_user(self, phone, password):
        """
        Creates and saves a User with the given phone and password
        """
        if not phone or not password:
            raise ValueError('Users must have an phone and password')

        user = self.model(phone=phone.lower())
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password):
        """
        Creates and saves a superuser with the given phone and password
        """
        user = self.create_user(phone=phone,
                                password=password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MainUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with phone .
    """
    phone = models.CharField(max_length=200, blank=True, null=True, unique=True, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True, null=True, unique=True, db_index=True)
    # fb_id = models.CharField(max_length=200, blank=True, null=True, unique=True, db_index=True)
    # insta_id = models.CharField(max_length=200, blank=True, null=True, unique=True, db_index=True)
    # vk_id = models.CharField(max_length=200, blank=True, null=True, unique=True, db_index=True)
    # languages = models.ManyToManyField('Language')
    language = models.IntegerField(choices=LANGUAGES, default=RUSSIAN)

    avatar = models.ImageField(upload_to=avatar_upload, blank=True, null=True)
    avatar_big = models.ImageField(upload_to=avatar_upload, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    review = models.FloatField(blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    #   for one signal notifications
    player_ids = ArrayField(models.CharField(max_length=255, blank=True, null=True, default=""), default=list)

    objects = MainUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.phone

    def __unicode__(self):
        return self.phone

    def __str__(self):
        return self.phone or self.email
        # or self.vk_id or self.fb_id or self.insta_id

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_admin

    def json(self, short=False, user=None):
        if not short:
            result = {
                "user_id": self.pk,
                "phone": self.hidden_phone(user),
                "name": self.name,
                "email": self.hidden_email(user),
                "avatar": get_url(self.avatar),
                "avatar_big": get_url(self.avatar_big) or get_url(self.avatar),
                # "languages": [l.name for l in self.languages.all()],
                "language_id": self.language,
                "language": self.get_language_display(),
                "review": self.review if self.review else None,
                # "reviews": [r.json(user) for r in self.reviews.all()],
                "verified": self.verified(),
                # 'game_setting': self.game_setting.json(user),
                "collections": self.collections.json(),
            }
        else:
            result = {
                "user_id": self.pk,
                "phone": self.hidden_phone(user),
                "email": self.hidden_email(user),
                "name": self.name,
                "avatar": get_url(self.avatar),
            }
        return result

    def owner_json(self, short=False):
        if not short:
            result = {
                "user_id": self.pk,
                "phone": self.phone,
                "name": self.name,
                "email": self.email,
                "avatar": get_url(self.avatar),
                "avatar_big": get_url(self.avatar_big) or get_url(self.avatar),
                # "languages": [l.name for l in self.languages.all()],
                "language_id": self.language,
                "language": self.get_language_display(),
                "review": self.review if self.review else None,
                # "reviews": [r.json(user=self) for r in self.reviews.all()],
                "verified": self.verified(),
                # 'game_setting': self.game_setting.json(),
            }
        else:
            result = {
                "user_id": self.pk,
                "phone": self.phone,
                "email": self.email,
                "name": self.name,
                "avatar": get_url(self.avatar),
            }
        return result

    def hidden_email(self, user=None):
        if self.email and user != self:
            return '*' * len(self.email)
        return self.email or None

    def hidden_phone(self, user=None):
        if self.phone and user != self:
            return self.phone[:(len(self.phone) - HIDE_LAST)] + '*' * HIDE_LAST
        return self.phone or None

    def verified(self):
        email = False
        if self.email:
            email = True

        phone = False
        if self.phone:
            phone = True

        return {
            "phone": phone,
            "email": email,
        }

    # def set_social_id(self, social_type, social_id):
    #     if social_type == "facebook" and not self.fb_id:
    #         self.fb_id = social_id
    #         self.save()
    #     elif social_type == "vk" and not self.vk_id:
    #         self.vk_id = social_id
    #         self.save()
    #     elif social_type == "insta" and not self.insta_id:
    #         self.insta_id = social_id
    #         self.save()
    #     elif social_type == "google" and not self.email:
    #         self.email = social_id
    #         self.save()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    # def save(self, *args, **kwargs):
    #     if self.contact_number is None and self.phone:
    #         self.contact_number = self.phone
    #     super(MainUser, self).save(*args, **kwargs)


class TokenLog(models.Model):
    """
    Token log model
    """
    token = models.CharField(max_length=500, blank=False, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tokens', null=False, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return u"Token {0} of user {1}".format(self.pk, self.user_id)

    class Meta:
        index_together = [
            ["token", "user"]
        ]


# @receiver(post_save, sender=MainUser)
# def create_game_settings(sender, instance, **kwargs):
#     """
#         Create game_settings for the user, if does not exist
#     """
#     _ = GameSetting.objects.get_or_create(owner=instance)


# class GameSetting(models.Model):
#     owner = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='game_setting', null=False, on_delete=models.CASCADE)
#     on_save = models.IntegerField(choices=ON_SAVE, default=ON_SAVE_SUM_30)
#     on_full = models.IntegerField(choices=ON_FULL, default=ON_FULL_OPEN_FOUR)
#     ace_allowed = models.BooleanField(default=True)
#     on_eggs = models.IntegerField(choices=ON_EGGS, default=ON_EGGS_OPEN_FOUR)
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return u"Game setting {0} of user {1}".format(self.pk, self.owner_id)
#
#     def json(self, user=None):
#         return {
#             "setting_id": self.pk,
#             "user_id": self.owner_id,
#             "on_save": self.on_save,
#             "on_save_display": self.get_on_save_display(),
#             "on_full": self.on_full,
#             "on_full_display": self.get_on_full_display(),
#             "ace_allowed": self.ace_allowed,
#             "on_eggs": self.on_eggs,
#             "on_eggs_display": self.get_on_eggs_display(),
#             "timestamp": dt_to_timestamp(self.timestamp),
#         }
#
#     class Meta:
#         ordering = ['timestamp']


