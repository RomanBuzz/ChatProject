from django import forms

from django.contrib.auth.models import User

from .models import ChatUser


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = ChatUser
        fields = ['avatar']
