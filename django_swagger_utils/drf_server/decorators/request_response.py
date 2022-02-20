# coding=utf-8
import importlib
import logging

logger = logging.getLogger('dsu.debug')


def get_defaults(app_name):
    from django_swagger_utils.drf_server.default.request_response import \
        REQUEST_RESPONSE_DECORATOR
    default_options = REQUEST_RESPONSE_DECORATOR

    from django_swagger_utils.drf_server.default.request_response import \
        SECURITY_DEFINITIONS
    security_definitions = SECURITY_DEFINITIONS

    if app_name:
        default_options = getattr(importlib.import_module(
            "%s.build.request_response.decorator_options" % app_name),
            "REQUEST_RESPONSE_DECORATOR")
        security_definitions = getattr(importlib.import_module(
            "%s.build.request_response.security_definitions" %
            app_name), "SECURITY_DEFINITIONS")
    return default_options, security_definitions


def configure_options(options, app_name):
    options = {} if options is None else options
    default_options, security_definitions = get_defaults(app_name)

    for key in list(default_options.keys()):
        if options.get(key) is None:
            options[key] = default_options[key]

    securities = options.get("SECURITY", [])
    options["PERMISSIONS_REQUIRED"] = []
    options["AUTHENTICATION_CLASSES"] = []
    options["SCOPES_REQUIRED"] = []

    for security in securities:

        security_def = security_definitions[security]
        options["SCOPES_REQUIRED"].extend(securities[security])
        options["PERMISSIONS_REQUIRED"].extend(
            security_def["PERMISSIONS_REQUIRED"])
        if security_def["TYPE"] != "API_KEY":
            options["AUTHENTICATION_CLASSES"].extend(
                security_def["AUTHENTICATION_CLASSES"])
        elif security_def["AUTHENTICATION_CLASSES"]:
            options["AUTHENTICATION_CLASSES"].extend(
                security_def["AUTHENTICATION_CLASSES"])
    return options


def _get_request(request):
    import json
    request_keys = ['LANGUAGE_CODE', 'method', 'content_params',
                    'path_info', 'path', 'COOKIES']
    request_info = {}
    for each in request_keys:
        request_info[each] = getattr(request, each, '')
    if 'auth' in request.__dict__:
        request_info['auth'] = str(request.auth)

    default_meta_keys = [
        'HTTP_REFERER',
        'SERVER_SOFTWARE',
        'UPSTART_EVENTS',
        'SCRIPT_NAME',
        'CONTENT_LENGTH',
        'HTTP_ORIGIN',
        'SERVER_PROTOCOL',
        'HTTP_COOKIE',
        'PATH_INFO',
        'UPSTART_INSTANCE',
        'HTTP_AUTHORITY',
        'HTTP_CACHE_CONTROL',
        'HTTP_HOST',
        'HTTP_ACCEPT',
        'SERVER_NAME',
        'HTTP_ACCEPT_LANGUAGE',
        'REQUEST_METHOD',
        'LANGUAGE',
        'HTTP_USER_AGENT',
        'LANG',
        'HTTP_CONNECTION',
        'HTTP_X_SOURCE',
        'REMOTE_ADDR',
        'CONTENT_TYPE',
        'TZ',
        'REMOTE_HOST',
        'HTTP_ACCEPT_ENCODING'
    ]

    from django.conf import settings
    meta_keys = getattr(settings, 'DSU_HEADER_META_KEYS_TO_LOG', default_meta_keys)

    request_meta_info = {}
    for each_key in meta_keys:
        if each_key in request.META:
            request_meta_info[each_key] = request.META[each_key]

    from copy import deepcopy
    from rest_framework.request import Request
    if isinstance(request, Request):
        request_data = request.data
    else:
        request_data = deepcopy(getattr(request, '_body', None))
    from rest_framework.exceptions import ParseError
    if request_data is not None:
        try:
            if not isinstance(request_data, dict):
                request_data = json.loads(request_data)
            if "clientKeyDetailsId" in request_data:
                request_data = request_data["data"]
                from django_swagger_utils.drf_server.utils.decorator.drf_json_parser import \
                    drf_json_parser
                request_data = drf_json_parser(request_data)
        except (ValueError, KeyError, TypeError, ParseError) as err:
            logger.error(err)
            pass

    log_data = {
        "basic_info": request_info,
        "meta": request_meta_info,
        "processed_request_data": mask_sensitive_info(request_data),
        "log_type": "api_request"
    }
    return log_data


def mask_sensitive_info(data):
    default_keys_to_mask = [
        "access_token",
        "code",
        "phone_number",
        "password",
        "refresh_token"
    ]

    from django.conf import settings
    keys_to_mask = getattr(settings, 'DSU_KEYS_TO_MASK', default_keys_to_mask)

    from copy import deepcopy
    data_copy = deepcopy(data)
    import json
    try:
        data_copy = json.loads(data_copy)
    except (ValueError, TypeError):
        pass

    if isinstance(data_copy, list):
        new_list = []
        for item in data_copy:
            new_list.append(mask_sensitive_info(item))
        return new_list

    elif isinstance(data_copy, dict):
        result_dict = {}
        for key in data_copy:
            value = data_copy[key]
            if isinstance(value, dict) or isinstance(value, list):
                value = mask_sensitive_info(value)

            if key in keys_to_mask:
                continue
            result_dict[key] = value
        return result_dict
    return data_copy


def request_response(
        options=None, app_name=None, operation_id=None, group_name=''):

    options = configure_options(options, app_name=app_name)

    def decorator(function):
        from django_swagger_utils.drf_server.decorators.wrap_exceptions import \
            wrap_exceptions
        from django_swagger_utils.drf_server.decorators.response_time import \
            response_time
        from rest_framework.decorators import api_view
        from rest_framework.decorators import authentication_classes
        from rest_framework.decorators import permission_classes
        from django_swagger_utils.drf_server.decorators.conditional_decorator import \
            conditional_decorator
        from oauth2_provider.decorators import protected_resource
        from rest_framework.decorators import parser_classes
        from rest_framework.decorators import renderer_classes

        @response_time(app_name=app_name, operation_id=operation_id)
        @wrap_exceptions()
        @api_view([options['METHOD']])  # Applying the specified request method
        @authentication_classes(options["AUTHENTICATION_CLASSES"])
        @permission_classes(options[
                                'PERMISSIONS_REQUIRED'])  # Applying the list of permissions specified
        @conditional_decorator(
            dec=protected_resource(scopes=options['SCOPES_REQUIRED']),
            condition=len(options['SCOPES_REQUIRED']))
        @parser_classes(options['PARSER_CLASSES'])
        @renderer_classes(options['RENDERER_CLASSES'])
        def handler(*args, **kwargs):
            from time import time
            from django_swagger_utils.drf_server.wrappers.request_response_wrapper import \
                RequestResponseWrapper

            st = time()
            request = args[0]
            request.app_name = app_name
            request.operation_id = operation_id

            from django_swagger_utils import local
            local.app_name = app_name
            local.operation_id = operation_id
            local.user_id = getattr(request.user, 'pk', '')

            from django.conf import settings
            if getattr(settings, 'LOG_DETAILED_REQUEST_RESPONSE', True):
                from django_swagger_utils.drf_server.decorators.response_time import \
                    handle_8kb_log_limit_response_log
                handle_8kb_log_limit_response_log(_get_request(request))

            req_res = RequestResponseWrapper(request=request, options=options,
                                             kwargs=kwargs)
            kwargs = req_res.pre_execution()

            check_custom_scopes(user=kwargs['user'], app_name=app_name,
                                operation_id=operation_id,
                                group_name=group_name)

            function_return_value = function(*args, **kwargs)
            return_value = req_res.post_execution(function_return_value)

            insert_last_access(request, app_name, operation_id)

            et = time()
            local.api_execution_time = et - st

            if getattr(settings, 'LOG_DSU_OLD_VERSION_LOGS', True):
                logger.debug({"APIExecutionTime": et - st})

            return return_value

        handler.__doc__ = function.__doc__
        return handler

    return decorator


def insert_last_access(request, app_name, operation_id):
    from django.conf import settings

    insert_last_access_required = getattr(
        settings, 'INSERT_LAST_ACCESS_REQUIRED', 'TRUE')

    if insert_last_access_required != 'TRUE':
        return

    user = request.user

    from django.contrib.auth.models import AnonymousUser
    if user.is_authenticated and not isinstance(user, AnonymousUser):
        from django_swagger_utils.models import LastAccess
        last_access_object, created = LastAccess.objects.get_or_create(
            app_name=app_name,
            operation_id=operation_id,
            user=user
        )
        last_access_object.save()
    return


def check_custom_scopes(user, app_name, operation_id, group_name):
    from django.conf import settings

    if group_name:
        abs_path = "{0}.views.{1}.{2}.__init__".format(
            app_name, group_name, operation_id)
    else:
        abs_path = "{0}.views.{1}.__init__".format(app_name, operation_id)

    custom_scopes = getattr(importlib.import_module(abs_path),
                            "CUSTOM_SCOPES", None)

    custom_scopes_check_func = getattr(
        settings, 'CUSTOM_SCOPES_CHECK_FUNCTION', None)
    if custom_scopes_check_func:
        func_ = getattr(importlib.import_module(
            ".".join(custom_scopes_check_func.split(".")[:-1])),
            custom_scopes_check_func.split(".")[-1])
        func_(user, custom_scopes)

    return
