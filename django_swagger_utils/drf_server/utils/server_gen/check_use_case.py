# coding=utf-8
import importlib
import json
from django_swagger_utils.core.utils.case_convertion import to_camel_case


def get_tests_dir_path_for_dsu_version_one(
    base_dir, app_name, group_name, operation_name):
    if group_name:
        tests_dir_path = base_dir + "/" + app_name + "/tests/views/" + \
                         group_name + "/" + operation_name + "/"
    else:
        tests_dir_path = base_dir + "/" + app_name + "/tests/views/" + \
                         operation_name + "/"
    return tests_dir_path


def get_tests_dir_path_for_dsu_version_zero(
    base_dir, app_name, group_name, operation_name):
    if group_name:
        tests_dir_path = base_dir + "/" + app_name + "/views/" + \
                         group_name + "/" + operation_name + "/tests/"
    else:
        tests_dir_path = base_dir + "/" + app_name + "/views/" + \
                         operation_name + "/tests/"
    return tests_dir_path


def get_views_tests_import_path_for_dsu_version_one(
    app_name, group_name, operation_name, test_case):
    if group_name:
        import_str = "%s.tests.views.%s.%s.%s" % (
            app_name, group_name, operation_name, test_case)
    else:
        import_str = "%s.tests.views.%s.%s" % (
            app_name, operation_name, test_case)
    return import_str


def get_views_tests_import_path_for_dsu_version_zero(
    app_name, group_name, operation_name, test_case):
    if group_name:
        import_str = "%s.views.%s.%s.tests.%s" % (
            app_name, group_name, operation_name, test_case)
    else:
        import_str = "%s.views.%s.tests.%s" % (
            app_name, operation_name, test_case)
    return import_str


def get_snapshot_import_path_for_dsu_version_one(
    app_name, group_name, operation_name, test_case):
    if group_name:
        snapshot_import = \
            "%s.tests.views.%s.%s.snapshots.snap_%s" % (
                app_name, group_name, operation_name,
                test_case)
    else:
        snapshot_import = \
            "%s.tests.views.%s.snapshots.snap_%s" % (
                app_name, operation_name, test_case)
    return snapshot_import


def get_snapshot_import_path_for_dsu_version_zero(
    app_name, group_name, operation_name, test_case):
    if group_name:
        snapshot_import = \
            "%s.views.%s.%s.tests.snapshots.snap_%s" % (
                app_name, group_name, operation_name, test_case)
    else:
        snapshot_import = \
            "%s.views.%s.tests.snapshots.snap_%s" % (
                app_name, operation_name, test_case)
    return snapshot_import


def check_use_case(default_test_case, kwargs, app_name, operation_name,
                   group_name=''):
    from django.conf import settings
    from django_swagger_utils.drf_server.constants.enums import \
        CleanCodeViewsTestsVersion
    base_dir = settings.BASE_DIR
    django_swagger_utils_settings = settings.SWAGGER_UTILS
    try:
        dsu_version = django_swagger_utils_settings['APPS'][app_name][
            'dsu_version']
    except KeyError:
        dsu_version = CleanCodeViewsTestsVersion.VERSION_ZERO.value

    if dsu_version == CleanCodeViewsTestsVersion.VERSION_ONE.value:
        tests_dir_path = get_tests_dir_path_for_dsu_version_one(
            base_dir, app_name, group_name, operation_name)
    else:
        tests_dir_path = get_tests_dir_path_for_dsu_version_zero(
            base_dir, app_name, group_name, operation_name)

    from django_swagger_utils.drf_server.utils.server_gen.get_test_cases_dict \
        import get_test_cases_dict
    test_cases_dict = get_test_cases_dict(tests_dir_path, operation_name)
    for test_case, test_case_dict in list(test_cases_dict.items()):
        try:

            if dsu_version == CleanCodeViewsTestsVersion.VERSION_ONE.value:
                import_str = get_views_tests_import_path_for_dsu_version_one(
                    app_name, group_name, operation_name, test_case)
            else:
                import_str = get_views_tests_import_path_for_dsu_version_zero(
                    app_name, group_name, operation_name, test_case)

            try:
                test_case_data = getattr(importlib.import_module(import_str),
                                         "TEST_CASE")
            except AttributeError:
                # For backward compatibility
                test_case_data = getattr(importlib.import_module(import_str),
                                         "test_case")

            test_case_request_data = test_case_data["request"]
            request_body = test_case_request_data["body"]
            try:
                request_body = json.loads(request_body)
            except ValueError as err:
                request_body = None
            if not test_case_data.get("response"):
                # Assuming testcase responses are available in snapshots
                try:
                    if dsu_version == CleanCodeViewsTestsVersion.VERSION_ONE.value:
                        snapshot_import = get_snapshot_import_path_for_dsu_version_one(
                            app_name, group_name, operation_name, test_case)
                    else:
                        snapshot_import = get_snapshot_import_path_for_dsu_version_zero(
                            app_name, group_name, operation_name, test_case)
                    snapshots = getattr(
                        importlib.import_module(snapshot_import), "snapshots")
                    camel_case_operation_name = to_camel_case(operation_name)
                    key = "{}{}APITestCase::test_case %s".format(
                        to_camel_case(test_case), camel_case_operation_name)
                    test_case_data['response'] = dict()
                    for i in ('body', 'status', 'header_params'):
                        test_case_data['response'][i] = snapshots[key % i]
                except ImportError:
                    pass
            if not kwargs["request_query_params"]:
                kwargs["request_query_params"] = {}
            if not kwargs["request_headers_obj"]:
                kwargs["request_headers_obj"] = {}
            if test_case_request_data == default_test_case['request']:
                default_test_case = test_case_data
            if request_body == kwargs["request_data"] and \
                test_case_request_data["query_params"] == kwargs[
                "request_query_params"] and \
                test_case_request_data["header_params"] == kwargs[
                "request_headers_obj"]:
                path_params_count = 0
                for path_param, path_param_value in list(
                    test_case_request_data[
                        "path_params"].items()):
                    if kwargs.get(path_param) == path_param_value:
                        path_params_count += 1
                if len(test_case_request_data[
                           "path_params"]) == path_params_count:
                    default_test_case = test_case_data
                    break
        except (ImportError, AttributeError):
            pass

    return default_test_case
