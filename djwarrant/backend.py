"""Custom Django authentication backend"""
import abc

from boto3.exceptions import Boto3Error
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils.six import iteritems

from warrant import Cognito
from .utils import cognito_to_dict


class CognitoUser(Cognito):
    user_class = get_user_model()
    # Mapping of Cognito User attribute name to Django User attribute name
    COGNITO_ATTR_MAPPING = getattr(settings, 'COGNITO_ATTR_MAPPING',
                                   {
                                       'email': 'email',
                                       'given_name': 'first_name',
                                       'family_name': 'last_name',
                                   }
                                   )

    def get_user_obj(self, username=None, attribute_list=[], metadata={}, attr_map={}):
        user_attrs = cognito_to_dict(
            attribute_list, CognitoUser.COGNITO_ATTR_MAPPING)
        django_fields = [
            f.name for f in CognitoUser.user_class._meta.get_fields()]
        extra_attrs = {}
        for k, v in list(user_attrs.items()):
            if k not in django_fields:
                extra_attrs.update({k: user_attrs.pop(k, None)})
        if getattr(settings, 'COGNITO_CREATE_UNKNOWN_USERS', True):
            user, created = CognitoUser.user_class.objects.update_or_create(
                username=username,
                defaults=user_attrs)
        else:
            try:
                user = CognitoUser.user_class.objects.get(username=username)
                for k, v in iteritems(user_attrs):
                    setattr(user, k, v)
                user.save()
            except CognitoUser.user_class.DoesNotExist:
                user = None
        if user:
            for k, v in extra_attrs.items():
                setattr(user, k, v)
        return user


class AbstractCognitoBackend(ModelBackend):
    __metaclass__ = abc.ABCMeta

    UNAUTHORIZED_ERROR_CODE = 'NotAuthorizedException'

    USER_NOT_FOUND_ERROR_CODE = 'UserNotFoundException'

    COGNITO_USER_CLASS = CognitoUser

    @abc.abstractmethod
    def authenticate(self, username=None, password=None):
        """
        Authenticate a Cognito User
        :param username: Cognito username
        :param password: Cognito password
        :return: returns User instance of AUTH_USER_MODEL or None
        """
        cognito_user = CognitoUser(
            settings.COGNITO_USER_POOL_ID,
            settings.COGNITO_APP_ID,
            access_key=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            secret_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
            user_pool_region=getattr(settings, 'AWS_REGION', None),
            username=username)
        try:
            cognito_user.authenticate(password)
        except (Boto3Error, ClientError) as e:
            return self.handle_error_response(e)
        user = cognito_user.get_user()
        if user:
            user.access_token = cognito_user.access_token
            user.id_token = cognito_user.id_token
            user.refresh_token = cognito_user.refresh_token

        return user

    def handle_error_response(self, error):
        error_code = error.response['Error']['Code']
        if error_code in [
            AbstractCognitoBackend.UNAUTHORIZED_ERROR_CODE,
            AbstractCognitoBackend.USER_NOT_FOUND_ERROR_CODE
        ]:
            return None
        raise error


class CognitoBackend(AbstractCognitoBackend):
    def authenticate(self, request, username=None, password=None):
        """
        Authenticate a Cognito User and store an access, ID and
        refresh token in the session.
        """
        user = super(CognitoBackend, self).authenticate(
            username=username, password=password)
        if user:
            request.session['ACCESS_TOKEN'] = user.access_token
            request.session['ID_TOKEN'] = user.id_token
            request.session['REFRESH_TOKEN'] = user.refresh_token
            request.session.save()
        return user

    def register(self, username,
                 password,
                 email,
                 first_name,
                 last_name):
        '''Register user with cognito
        :param username: Cognito Username
        :param password: Cognito Password
        :param email: Email
        :param first_name: First name
        :param last_name: Last name
        :returns: Response from Cognito
        '''

        cognito_user = CognitoUser(
            settings.COGNITO_USER_POOL_ID,
            settings.COGNITO_APP_ID,
            access_key=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            secret_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
            user_pool_region=getattr(settings, 'AWS_REGION', None),
            username=username)

        try:
            cognito_user.add_base_attributes(**{'given_name': first_name,
                                                'family_name': last_name,
                                                'email': email})
            response = cognito_user.register(username, password)
        except (Boto3Error, ClientError) as e:
            return self.handle_error_response(e)

        return response

    def validate_user(self, confirmation_code, username):
        '''Validate user account with confirmation code sent by AWS
        :param confirmation_code: Confirmation code received from Cognito
        :param username: Cognito Username
        '''
        cognito_user = CognitoUser(
            settings.COGNITO_USER_POOL_ID,
            settings.COGNITO_APP_ID,
            access_key=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            secret_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
            user_pool_region=getattr(settings, 'AWS_REGION', None),
            username=username)
        cognito_user.confirm_sign_up(confirmation_code,
                                     username=username)
