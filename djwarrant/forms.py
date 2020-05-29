from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=200,required=True)
    last_name = forms.CharField(max_length=200,required=False)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=30,required=False)
    gender = forms.ChoiceField(choices=(('female','Female'),('male','Male')),required=False)
    address = forms.CharField(max_length=200,required=False)
    preferred_username = forms.CharField(max_length=200,required=False)
    api_key = forms.CharField(max_length=200, required=False)
    api_key_id = forms.CharField(max_length=200, required=False)


class APIKeySubscriptionForm(forms.Form):
    plan = forms.ChoiceField(required=True)

    def __init__(self, plans=[], users_plans=[], *args, **kwargs):
        self.base_fields['plan'].choices = [(p.get('id'),p.get('name')) for p in plans if not p.get('id') in users_plans]
        super(APIKeySubscriptionForm, self).__init__(*args, **kwargs)

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True)
    first_name = forms.CharField(max_length=200, required=True)
    last_name = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=30, required=False)
    gender = forms.ChoiceField(choices=(('female', 'Female'), ('male', 'Male')), required=False)
    address = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2',
                  'phone_number', 'gender', 'address',)