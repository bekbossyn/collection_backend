# -*- coding: utf-8 -*-
import requests

from utils.time_utils import dt_to_timestamp
from . import tasks

from django.conf import settings
from django.contrib.auth.hashers import make_password

from django.core.files import File
from django.db import models
from django.template.loader import render_to_string

from io import BytesIO
# from utils import mobizonproxy
from utils.messages import REGISTRATION_COMPLETE, PASSWORD_EMAIL_RESET
from utils.upload import avatar_upload_v2, get_random_name


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


class ActivationManager(models.Manager):
    """
    Custom manager for Activation model
    """

    def create_social_code(self, email, phone, password):
        """
        Creates activation code and sends SMS via mobizon.kz service.
        Stores hashed password.
        TODO: Logging
        """
        # code = "4512"
        code = "1111"
        activation = Activation(phone=phone,
                                email=email,
                                to_reset=False,
                                password=make_password(password),
                                code=code)
        activation.save()
        return activation

    def create_email_signup_code(self, email, password):
        """
        Creates activation code and sends SMS via mobizon.kz service.
        Stores hashed password.
        TODO: Logging
        """
        # code = "%0.4d" % random.randint(0, 9999)
        code = "1111"
        activation = Activation(email=email,
                                to_reset=False,
                                password=make_password(password),
                                code=code)
        activation.save()
        return activation

    def create_email_reset_code(self, email, new_password):
        code = "1111"
        activation = Activation(email=email,
                                to_reset=True,
                                to_change_phone=False,
                                to_change_email=False,
                                password=make_password(new_password),
                                code=code)
        activation.save()
        return activation

    def create_phone_signup_code(self, phone, password):
        """
        Creates activation code and sends SMS via mobizon.kz service.
        Stores hashed password.
        TODO: Logging
        """
        code = "1111"

        # if phone in ["+77753721232", "+77752470125", "+77074443333", "+77076799939"]:
        #     code = "4512"
        # else:
        #     code = "%0.4d" % random.randint(0, 9999)

        # mobizonproxy.send_sms(phone, text=u"{} - Код активации для Pillowz365".format(code))
        activation = Activation(phone=phone,
                                to_reset=False,
                                password=make_password(password),
                                code=code)
        activation.save()
        return activation

    def create_code_without_password(self, phone):
        """
        Creates activation code and sends SMS via mobizon.kz service.
        Stores hashed password.
        TODO: Logging
        """

        code = "1111"

        # if phone in ["+77753721232", "+77752470125", "+77074443333"]:
        #     code = "4512"
        # else:
        #     code = "%0.4d" % random.randint(0, 9999)
        #     mobizonproxy.send_sms(phone, text=u"{} - Код активации для Pillowz365".format(code))
        activation = Activation(phone=phone,
                                to_reset=False,
                                password=make_password(code),
                                code=code)
        activation.save()
        return activation

    def create_phone_change_code(self, phone, email, new_phone):
        """
        Creates activation code and sends SMS via mobizon.kz service.
        Stores hashed password.
        TODO: Logging
        """

        code = "1111"

        # if new_phone in ["+77753721232", "+77752470125", "+77074443333"]:
        #     code = "4512"
        # else:
        #     code = "%0.4d" % random.randint(0, 9999)
        #     mobizonproxy.send_sms(new_phone, text=u"{} - Код подтверждения для Pillowz365".format(code))
        activation = Activation(phone=phone,
                                email=email,
                                new_phone=new_phone,
                                to_reset=False,
                                to_change_phone=True,
                                to_change_email=False,
                                password=make_password(code),
                                code=code)
        activation.save()
        return activation

    def create_email_change_code(self, email, phone, new_email):
        """
        Creates activation code and sends SMS via mobizon.kz service.
        Stores hashed password.
        TODO: Logging
        """

        code = "1111"

        # if new_phone in ["+77753721232", "+77752470125", "+77074443333"]:
        #     code = "4512"
        # else:
        #     code = "%0.4d" % random.randint(0, 9999)
        #     mobizonproxy.send_sms(new_email, text=u"{} - Код подтверждения для Pillowz365".format(code))
        activation = Activation(email=email,
                                phone=phone,
                                new_email=new_email,
                                to_reset=False,
                                to_change_email=True,
                                to_change_phone=False,
                                password=make_password(code),
                                code=code)
        activation.save()
        return activation

    def create_reset_code(self, phone, new_password):
        """
        Creates activation code and sends SMS via mobizon.kz service.
        Stores hashed password.
        TODO: Logging
        """

        code = "1111"

        # if phone in ["+77753721232", "+77752470125", "+77074443333"]:
        #     code = "4512"
        # else:
        #     code = "%0.4d" % random.randint(0, 9999)
        #     mobizonproxy.send_sms(phone, text=u"{} - Код активации для Pillowz365".format(code))
        activation = Activation(phone=phone,
                                to_reset=True,
                                password=make_password(new_password),
                                code=code)
        activation.save()
        return activation


class Activation(models.Model):
    """
    Stores information about activations
    """
    name = models.CharField(max_length=255, blank=True, null=True)

    phone = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    new_phone = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    email = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    new_email = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    password = models.CharField(max_length=100, blank=False, db_index=True)
    code = models.CharField(max_length=100, blank=False, db_index=True)
    used = models.BooleanField(default=False, db_index=True)

    to_reset = models.BooleanField(default=False, db_index=True)
    to_change_phone = models.BooleanField(default=False, db_index=True)
    to_change_email = models.BooleanField(default=False, db_index=True)

    objects = ActivationManager()

    # fb_id = models.CharField(max_length=200, blank=True, null=True)
    # insta_id = models.CharField(max_length=200, blank=True, null=True)
    # vk_id = models.CharField(max_length=200, blank=True, null=True)
    avatar = models.ImageField(upload_to=avatar_upload_v2, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def send_email(self):
        message = render_to_string('emails/activation.html',
                                   context={'code': self.code})
        tasks.email(to=self.email, subject=REGISTRATION_COMPLETE["ru"], message=message)

    def send_reset_email(self):
        message = render_to_string('emails/activation.html',
                                   context={'code': self.code,
                                            'reset': True})
        tasks.email(to=self.email, subject=PASSWORD_EMAIL_RESET["ru"], message=message)

    def send_sms(self):
        self.code = "1111"
        # if self.phone in ["+77753721232", "+77752470125", "+77074443333", "+77076799939"]:
        #     self.code = "4512"
        # mobizonproxy.send_sms(self.phone, text=u"{} - Код активации для Pillowz365".format(self.code))

    def __unicode__(self):
        return u"{0} {1}".format(self.phone, self.code)

    # def set_social_id(self, social_type, social_id):
    #     if social_type == "facebook" and not self.fb_id:
    #         self.fb_id = social_id
    #     elif social_type == "vk" and not self.vk_id:
    #         self.vk_id = social_id
    #     elif social_type == "insta" and not self.insta_id:
    #         self.insta_id = social_id
    #     elif social_type == "google" and not self.email:
    #         self.email = social_id

    def handle_avatar(self, url, save=True):
        """
        Downloads image from url & saves to local storage
        """
        response = requests.get(url)
        if response.status_code == 200:
            fp = BytesIO(response.content)
            ext = url.split('.')[-1]
            ext = ext if ext in ["png", "jpg", "gif", "jpeg"] else "jpg"
            filename = "{}.{}".format(get_random_name(), ext)
            self.avatar.save(filename, File(fp), save=save)

    class Meta:
        ordering = ['-timestamp']
        index_together = [
            ["phone", "email", "used"]
        ]


class Exchange(models.Model):
    sending = models.FloatField(blank=True, null=True)
    receiving = models.FloatField(blank=True, null=True)
    data_and_time = models.CharField(max_length=70, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u"id {0} date and time {1}".format(self.pk, self.data_and_time)

    def json(self):
        return {
            "id": self.pk,
            "timestamp": dt_to_timestamp(self.timestamp),
            "sending": self.sending,
            "receiving": self.receiving,    # Halyk bank course
            "data_and_time": self.data_and_time,
        }

    class Meta:
        ordering = ['timestamp']

