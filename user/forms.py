# -*- coding: utf-8 -*-
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm

from user.models import MainUser


class MainUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(MainUserCreationForm, self).__init__(*args, **kwargs)

    class Meta(UserCreationForm.Meta):
        model = MainUser
        fields = '__all__'


class MainUserChangeForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(MainUserChangeForm, self).__init__(*args, **kwargs)

    class Meta(UserChangeForm.Meta):
        model = MainUser
        fields = '__all__'
