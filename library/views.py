from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, FormView
from .forms import RegisterForm, AccountVerificationForm
from djwarrant.backend import CognitoBackend
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

# Create your views here.


def index(request):
    return HttpResponse('Home Page')


class AccountVerification(FormView):
    template_name = 'account_verification.html'
    form_class = AccountVerificationForm

    def get_initial(self):
        initial = super().get_initial()
        initial['username'] = self.kwargs.get('username', '')

        return initial

    def get_success_url(self):
        return resolve_url('/')

    def form_valid(self, form):
        cognito = CognitoBackend()

        try:
            resp = cognito.validate_user(**form.user)
            print(resp)
        except Exception as e:
            print(e)
            pass

        return super().form_valid(form)


class Register(FormView):
    template_name = 'register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        cognito = CognitoBackend()

        try:
            resp = cognito.register(**form.user)
        except Exception as e:
            if "User already exists" in str(e):
                form.errors['username'] = form.error_class(
                    ['The provided username is already in use'])
                return self.form_invalid(form)

            elif "Password did not conform with the policy" in str(e):
                forms.errors['username'] = form.error_class(
                    ['The password provided is invalid'])
                return self.form_invalid(form)

            else:
                raise(e)

        return HttpResponseRedirect(reverse('account_verification',
                                            kwargs={'username': form.user['username']}))
