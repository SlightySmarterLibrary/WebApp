from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.Register.as_view(), name='register'),
    path('account_verification/', views.AccountVerification.as_view()),
    path('account_verification/<slug:username>/', views.AccountVerification.as_view(),
         name='account_verification'),
    path('browse/', views.browse, name='browse'),
]
