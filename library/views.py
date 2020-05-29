from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, FormView
from .forms import RegisterForm, AccountVerificationForm
from djwarrant.backend import CognitoBackend
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.conf import settings
import boto3

# Create your views here.


def index(request):
    return HttpResponse('Home page')


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


def browse(request):
    # Get access token
    client = boto3.client('cognito-identity',
                          region_name=settings.AWS_REGION_NAME)
    # Get credentials for authenticated user
    try:
        resp = client.get_id(IdentityPoolId=settings.COGNITO_IDENTITY_POOL_ID,
                             Logins={
                                 'cognito-idp.'+settings.AWS_REGION_NAME+'.amazonaws.com/'+settings.COGNITO_USER_POOL_ID: request.session['ID_TOKEN']
                             })
        resp = client.get_credentials_for_identity(IdentityId=resp['IdentityId'],
                                                   Logins={
                                                       'cognito-idp.'+settings.AWS_REGION_NAME+'.amazonaws.com/'+settings.COGNITO_USER_POOL_ID: request.session['ID_TOKEN']
        })
    # Otherwise, get credential for unauthenticated user
    except:
        resp = client.get_id(IdentityPoolId=settings.COGNITO_IDENTITY_POOL_ID)
        resp = client.get_credentials_for_identity(
            IdentityId=resp['IdentityId'])

    secretKey = resp['Credentials']['SecretKey']
    accessKey = resp['Credentials']['AccessKeyId']
    sessionToken = resp['Credentials']['SessionToken']

    client = boto3.client('dynamodb', aws_access_key_id=accessKey,
                          aws_secret_access_key=secretKey, aws_session_token=sessionToken,
                          region_name=settings.AWS_REGION_NAME)
    response = client.scan(TableName=settings.DYNAMODB_BOOKS)
    booklist = sorted(response['Items'], key=lambda k: int(k['id']['S']))
    paginator = Paginator(booklist, 20)

    page = request.GET.get('page')
    books = paginator.get_page(page)

    return render(request, 'browse.html', {'books': books})
