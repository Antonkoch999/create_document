from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

from .models import Client


class MyAuthenticationForm(AuthenticationForm):
    """Adding recaptcha in template."""

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)


class UserRegistrationForm(forms.ModelForm):
    """Create form for register."""

    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        """Check password."""
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class InputTextForms(forms.Form):
    """Create form for adding data for new document."""

    number_document = forms.CharField(max_length=2)
    data_creation = forms.CharField(max_length=10)
    name_of_work = forms.CharField(max_length=255)
    count_hours = forms.CharField(max_length=20)
    cost = forms.CharField(max_length=30)


class CreateClientForm(forms.ModelForm):
    """Create form for Client."""

    class Meta:
        model = Client
        fields = '__all__'
