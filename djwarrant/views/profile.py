from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

try:
    from django.urls import reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib import messages
from django.contrib.auth.views import LogoutView as DJLogoutView
from django.conf import settings
from django.shortcuts import render

from djwarrant.utils import get_cognito
from djwarrant.forms import ProfileForm

from ..forms import SignUpForm

from warrant import Cognito

class TokenMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('REFRESH_TOKEN'):
            return self.handle_no_permission()
        return super(TokenMixin, self).dispatch(
            request, *args, **kwargs)

class GetUserMixin(object):

    def get_user(self):
        c = get_cognito(self.request)
        return c.get_user(attr_map=settings.COGNITO_ATTR_MAPPING)


class ProfileView(LoginRequiredMixin,TokenMixin,GetUserMixin,TemplateView):
    template_name = 'warrant/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['user'] = self.get_user()
        return context


class UpdateProfileView(LoginRequiredMixin,TokenMixin,GetUserMixin,FormView):
    template_name = 'warrant/update-profile.html'
    form_class = ProfileForm

    def get_success_url(self):
        return reverse_lazy('dw:profile')

    def get_initial(self):
        u = self.get_user()
        return u.__dict__.get('_data')
    
    def form_valid(self, form):
        c = get_cognito(self.request)
        c.update_profile(form.cleaned_data,settings.COGNITO_ATTR_MAPPING)
        messages.success(self.request,'You have successfully updated your profile.')
        return super(UpdateProfileView, self).form_valid(form)


class LogoutView(DJLogoutView):

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        request.session.delete()
        return super(LogoutView, self).dispatch(request, *args, **kwargs)


class SignUpView(FormView):
    template_name = 'warrant/signup.html'
    form_class = SignUpForm

    def get_success_url(self):
        return reverse_lazy('dw:login')

    def form_valid(self, form):
        username = form.cleaned_data.pop('username')
        password = form.cleaned_data.pop('password1')
        del form.cleaned_data['password2']
        form.cleaned_data['given_name'] = form.cleaned_data.pop('first_name')
        form.cleaned_data['family_name'] = form.cleaned_data.pop('last_name')
        c = Cognito(settings.COGNITO_USER_POOL_ID, settings.COGNITO_APP_ID)
        c.add_base_attributes(**form.cleaned_data)
        c.register(username, password)
        messages.success(self.request, 'You have successfully signed up.')
        return super(SignUpView, self).form_valid(form)