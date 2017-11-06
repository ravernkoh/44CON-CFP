from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required - Input a valid email address.')
    name = forms.CharField(max_length=128, required=True, help_text='Required - Preferably your full name.')
    country = forms.CharField(max_length=48, required=True, help_text='Required - Your country of residence.')
    affiliation = forms.CharField(max_length=32, required=False, help_text='Optional - Your employer or place of study.')

    class Meta:
        model = User
        fields = ('username', 'name', 'country', 'affiliation', 'email', 'password1', 'password2', )
