
from django.contrib.auth import views as auth_views
from django.urls import re_path

from .views import ProfileView,UpdateProfileView,MySubsriptions,\
    AdminListUsers,AdminSubscriptions,LogoutView, SignUpView

from . import views

app_name = 'dw'

urlpatterns = (
    re_path(r'^login/$', auth_views.LoginView.as_view(template_name='warrant/login.html'), name='login'),
    re_path(r'^logout/$', LogoutView.as_view(template_name='warrant/logout.html'), name='logout'),
    re_path(r'^signup/$', SignUpView.as_view(), name='signup'),
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    re_path(r'^profile/$', ProfileView.as_view(),name='profile'),
    re_path(r'^profile/update/$', UpdateProfileView.as_view(),name='update-profile'),
    re_path(r'^profile/subscriptions/$', MySubsriptions.as_view(),name='subscriptions'),
    re_path(r'^admin/cognito-users/$', AdminListUsers.as_view(),name='admin-cognito-users'),
    re_path(r'^admin/cognito-users/(?P<username>[-\w]+)$', AdminSubscriptions.as_view(),name='admin-cognito-user')
)