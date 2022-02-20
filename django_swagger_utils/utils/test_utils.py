import pytest


class InvalidRequestMethod(Exception):
    pass


# from snapshottest.django import TestRunner
# from snapshottest.unittest import TestCase as uTestCase


# class DiscoverRunner(TestRunner):
#     def __init__(self, snapshot_update=False, **kwargs):
#         super(DiscoverRunner, self).__init__(**kwargs)
#         uTestCase.snapshot_should_update = snapshot_update
#

class TestUtils:
    """
        SECURITY = {
            "oauth": {
                "scopes": ["write"]
            }
        }
    """

    API_USER_CONFIG = {
        "username": "apiuser",
        "email": "apiuser@example.com",
        "password": "password",
        "is_staff": True
    }
    URL_SUFFIX = ""
    APP_NAME = ""
    REQUEST_METHOD = ""
    OAUTH_APPLICATION_NAME = "oauth-application"
    SECURITY = {}
    SNAPSHOT_HEADERS = False

    @pytest.fixture
    def api_user(self):
        user = self._get_or_create_user()
        return user

    def _get_or_create_user(self):
        from django.contrib.auth import get_user_model
        user_model = get_user_model()
        username = self.API_USER_CONFIG['username']
        password = self.API_USER_CONFIG['password']
        email = self.API_USER_CONFIG['email']
        is_staff = self.API_USER_CONFIG['is_staff']

        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            user = user_model.objects.create_user(
                username,
                email,
                password,
                is_staff=is_staff
            )
        return user

    def _create_oauth_client(self, api_user):
        from oauth2_provider.models import Application
        try:
            app = Application.objects.get(name=self.OAUTH_APPLICATION_NAME)
        except Application.DoesNotExist:
            app = Application.objects.create(
                name=self.OAUTH_APPLICATION_NAME,
                redirect_uris="http://example.com",
                client_id='client_id',
                client_secret='client_secret',
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
                user=api_user,
                skip_authorization=True
            )
        return app

    def _create_oauth_tokens(self, api_user, oauth_app):
        import datetime
        from django.utils import timezone
        from oauth2_provider.models import AccessToken

        access_token = self._generate_token()
        expires = timezone.now() + datetime.timedelta(days=1000)
        scopes = self.SECURITY.get("oauth", {}).get("scopes", [])

        scopes_as_str = " ".join(scopes)

        access_token_object = AccessToken(
            user=api_user, token=access_token,
            application=oauth_app,
            expires=expires,
            scope=scopes_as_str
        )
        access_token_object.save()
        return access_token_object.token

    def _create_auth_token(self, api_user):
        oauth_app = self._create_oauth_client(api_user=api_user)
        access_token = \
            self._create_oauth_tokens(api_user=api_user, oauth_app=oauth_app)

        return access_token

    def _add_path_params(self, path_params):
        url_suffix = self.URL_SUFFIX.format(**path_params)
        url = '/api/%s/%s' % (self.APP_NAME, url_suffix)
        return url

    @staticmethod
    def _add_query_params(url, query_params):
        import urllib.parse
        url += "?" + urllib.parse.urlencode(query_params, doseq=True)
        return url

    @staticmethod
    def _create_api_client():
        from rest_framework.test import APIClient
        client = APIClient()
        return client

    def _set_api_credentials_based_on_authentication_type(
        self, api_client, api_user, header_params, query_params):
        if "oauth" in self.SECURITY:
            auth_token = self._create_auth_token(api_user=api_user)
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + auth_token)
        elif "basic" in self.SECURITY:
            import base64
            auth_value = 'Basic '.encode() + base64.b64encode(
                '{}:{}'.format(
                    self.API_USER_CONFIG["username"],
                    self.API_USER_CONFIG["password"]
                ).encode()
            )
            api_client.credentials(HTTP_AUTHORIZATION=auth_value)
        elif "apiKey" in self.SECURITY:
            if self.SECURITY["in"] == "header":
                header_params.update(
                    {
                        self.SECURITY["header_name"]: self.SECURITY["value"]
                    }
                )
            else:
                query_params.update(
                    {
                        self.SECURITY["name"]: self.SECURITY["value"]
                    }
                )

    def prepare_request_details(self, url, query_params, header_params):
        api_client = self._create_api_client()
        api_user = self._get_or_create_user()
        self._set_api_credentials_based_on_authentication_type(
            api_client=api_client, api_user=api_user,
            header_params=header_params, query_params=query_params
        )
        if query_params:
            url = self._add_query_params(url=url, query_params=query_params)
        return api_client, url, header_params

    def _invoke_http_method_call(self, api_client, url, body, header_params):
        import json
        if self.REQUEST_METHOD == "post":
            method = api_client.post
            data = json.dumps(body)
        elif self.REQUEST_METHOD == "get":
            method = api_client.get
            data = None
        elif self.REQUEST_METHOD == "delete":
            method = api_client.delete
            data = None
        elif self.REQUEST_METHOD == "put":
            method = api_client.put
            data = json.dumps(body)
        else:
            raise InvalidRequestMethod
        response = method(
            path=url,
            data=data,
            content_type='application/json',
            follow=False,
            **header_params
        )
        return response

    def make_api_call(self, body=None, query_params=None, path_params=None,
                      headers=None, snapshot=None):

        if body is None:
            body = {}
        if query_params is None:
            query_params = {}
        if path_params is None:
            path_params = {}
        if headers is None:
            headers = {}

        updated_body = self._prepare_body(body)
        url = self._add_path_params(path_params=path_params)

        api_client, url, header_params = self.prepare_request_details(
            url=url,
            query_params=query_params,
            header_params=headers
        )
        response = self._invoke_http_method_call(
            api_client=api_client, url=url, body=updated_body,
            header_params=header_params
        )

        self._assert_snapshots(response=response, snapshot=snapshot)
        return response

    @staticmethod
    def _prepare_body(body):
        import json
        from django.conf import settings
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        defaults = django_swagger_utils_settings["DEFAULTS"]

        if defaults.get("REQUEST_WRAPPING_REQUIRED", True):
            wrapped_request_data = {
                "data": "'" + json.dumps(body) + "'",
                "clientKeyDetailsId": 1
            }
        else:
            wrapped_request_data = body
        return wrapped_request_data

    @staticmethod
    def _generate_token():
        import string
        import random

        size = 30
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for _ in range(size))

    def _assert_snapshots(self, response, snapshot):
        import json

        snapshot.assert_match(
            str(response.status_code), 'status_code'
        )
        try:
            response_content = json.loads(response.content)
        except ValueError:
            response_content = response.content.strip()
        snapshot.assert_match(response_content, name='body')

        from django.conf import settings
        mock_x_ib_request_id = getattr(settings, 'MOCK_X_IB_REQUEST_ID')
        if "x-ib-request-id" in response._headers and mock_x_ib_request_id:
            response._headers["x-ib-request-id"] = (
                'X-IB-REQUEST-ID', '8324199f578948078718d7291f3cb514'
            )

        if self.SNAPSHOT_HEADERS:
            response._headers = self._sort_response_headers(response._headers)
            snapshot.assert_match(response._headers, name='header_params')

    @staticmethod
    def _sort_response_headers(response_headers):
        from collections import OrderedDict
        response_headers = OrderedDict(sorted(response_headers.items()))

        for attr, attr_values in list(response_headers.items()):
            if attr == 'allow':
                response_headers.pop(attr)
            else:
                response_headers[attr] = sorted(attr_values)

        return response_headers
