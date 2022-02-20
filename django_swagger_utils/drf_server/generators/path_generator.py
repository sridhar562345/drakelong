import json

from future import standard_library

from .conf import render

standard_library.install_aliases()


class PathGenerator(object):
    base_path = ""

    def __init__(self, app_name, dir_paths, path, path_name, parser,
                 group_name=''):
        self.app_name = app_name
        self.dir_paths = dir_paths
        self.path = path
        self.path_name = path_name
        self.parser = parser
        self.group_name = group_name

    def get_urls(self):
        path_method_dict, operation_ids = self.get_path_method_dict()
        view_environment_path_dict = self.view_environment_path_dict()
        return path_method_dict, view_environment_path_dict, operation_ids

    def view_environment_path_dict(self):
        path_name = self.path_name[1:]
        path_name = path_name.replace("/", "_")
        path_name = path_name.replace("{", "_")
        path_name = path_name.replace("}", "_")

        path_view_environment_dir_name = \
            self.dir_paths["view_environments_dir"] + "/" + path_name

        router_path = path_view_environment_dir_name + "/router.py"

        from django_swagger_utils.core.utils.convert_path_to_package_str import \
            convert_path_to_package_str
        package_import_str = convert_path_to_package_str(
            router_path, self.dir_paths['base_dir'])
        package_import_str = "from %s import %s" % (
            package_import_str, path_name)

        name_dict = {
            "view_environment_dir": path_view_environment_dir_name,
            "view_environment_router_path": router_path,
            "import_str": package_import_str,
            "path_name": path_name
        }

        return name_dict

    def get_method_path_url(self, method_name):
        path_url = self.path_name
        example_path_url = self.path_name
        all_path_parameters = self.get_all_parameters(method_name, "path")
        path_params_dict = {}
        for each_path_param in all_path_parameters:
            from django_swagger_utils.drf_server.fields.path_parameter_field import \
                path_param_field
            path_parameter_properties = path_param_field(each_path_param)
            path_url_regex = path_parameter_properties["param_url_regex"]
            example_url_regex = path_parameter_properties["example_url_regex"]
            path_url = path_url.replace("{%s}" % each_path_param["name"],
                                        path_url_regex)
            example_path_url = example_path_url.replace(
                "{%s}" % each_path_param["name"], example_url_regex)
            path_params_dict[each_path_param["name"]] = example_url_regex

        path_url = self.clean_path_url(path_url)
        example_path_url = self.clean_path_url(example_path_url)

        return path_url, example_path_url, path_params_dict

    def get_path_method_dict(self):
        path_method_dict = {}
        operation_ids = []
        for method_name, each_method in list(self.path.items()):
            if method_name != "parameters":

                self.group_name = each_method.get('x-group', '')
                path_url, example_path_url, path_params_dict = self.get_method_path_url(
                    method_name)

                method_dict = path_method_dict.get(path_url, {})
                operation_id = each_method["operationId"]
                operation_ids.append(operation_id)
                request_method = method_name.upper()

                # allowed skip url tag
                tags = each_method.get('tags', [])
                from django.conf import settings
                skip_url_tags = getattr(
                    settings, 'DJANGO_SWAGGER_UTILS_SKIP_URL_TAGS',
                    []
                )
                skip_tag_found = False
                for tag in tags:
                    if tag in skip_url_tags:
                        skip_tag_found = True
                        break
                if not skip_tag_found:
                    method_dict[request_method] = operation_id
                    path_method_dict[path_url] = method_dict

                endpoint_dict = self.get_endpoint_dict(method_name,
                                                       each_method)
                endpoint_dict["path_params"] = json.dumps(path_params_dict)
                self.generate_endpoint_file(endpoint_dict)
                self.generate_view_flies(endpoint_dict)
                testing_url = self.clean_path_url(self.path_name)
                self.generate_test_cases(endpoint_dict, testing_url, 1,
                                         snapshot=True)

        return path_method_dict, operation_ids

    @staticmethod
    def clean_path_url(source_url):
        path_url = source_url[1:]  # removing the first / from url
        from django.conf import \
            settings  # supporting non trailing slash based on settings, its backward campatible as well
        if settings.APPEND_SLASH and path_url[-1] != "/":
            path_url += "/"
        return path_url

    def get_endpoint_dict(self, method_name, each_method):
        operation_id = each_method["operationId"]
        custom_scopes = each_method.get("x-scopes", None)
        request_method = method_name.upper()
        request_wrapping = False if request_method in ["GET"] else True

        from django.conf import settings
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        defaults = django_swagger_utils_settings["DEFAULTS"]
        if request_wrapping:
            request_wrapping = defaults.get("REQUEST_WRAPPING_REQUIRED",
                                            request_wrapping)
        request_encryption = defaults.get("REQUEST_ENCRYPTION_REQUIRED", False)

        imports_list = [
            "from django_swagger_utils.drf_server.decorators.request_response import request_response",
            "from django_swagger_utils.drf_server.default.parser_mapping import PARSER_MAPPING",
            "from django_swagger_utils.drf_server.default.renderer_mapping import RENDERER_MAPPING",
        ]

        headers_dict = self.get_method_headers_dict(method_name, operation_id)
        query_params_dict = self.get_method_query_params_dict(method_name,
                                                              operation_id)
        path_params_dict = self.get_method_path_params_dict(method_name,
                                                            operation_id)
        body_param_dict = self.get_method_body_parameter_dict(method_name,
                                                              operation_id)
        consumes_dict = self.get_property_dict("consumes", each_method)
        produces_dict = self.get_property_dict("produces", each_method)
        security_dict = self.get_property_dict("security", each_method)

        responses_dict = self.get_responses_dict(each_method)

        endpoint_dict = {
            "app_name": self.app_name,
            "group_name": self.group_name,
            "operation_id": operation_id,
            "request_method": request_method,
            "request_wrapping": request_wrapping,
            "consumes": consumes_dict,
            "produces": produces_dict,
            "securities": security_dict,
            "request_query_params_serializer": "None",
            "request_query_params": {},
            "request_headers_serializer": "None",
            "request_headers_params": {},
            "request_path_params_serializer": "None",
            "default_request_path_params": {},
            "responses": {},
            "request_body_serializer": "None",
            "request_body_serializer_is_array": "False",
            "request_body_sample_json": "",
            "request_encryption": request_encryption,
            "custom_scopes": custom_scopes
        }

        if query_params_dict["request_query_params_serializer"]:
            endpoint_dict["request_query_params_serializer"] = \
                query_params_dict["request_query_params_serializer"]
            endpoint_dict["request_query_params"] = json.dumps(
                query_params_dict["request_query_params"])
            imports_list.append(query_params_dict[
                                    "request_query_params_serializer_import_str"])

        if headers_dict["request_headers_serializer"]:
            endpoint_dict["request_headers_serializer"] = \
                headers_dict["request_headers_serializer"]
            endpoint_dict["request_headers_params"] = json.dumps(
                headers_dict["request_headers_params"])
            imports_list.append(
                headers_dict["request_headers_serializer_import_str"])

        if path_params_dict['request_path_params_serializer']:
            endpoint_dict['request_path_params_serializer'] = path_params_dict[
                'request_path_params_serializer']
            endpoint_dict['default_request_path_params'] = json.dumps(
                path_params_dict['request_path_params'])
            imports_list.append(
                path_params_dict['request_path_params_serializer_import_str'])

        if body_param_dict:

            if body_param_dict["param_serializer_sample_json"]:
                endpoint_dict["request_body_sample_json"] = body_param_dict[
                    "param_serializer_sample_json"]

            if body_param_dict["param_serializer"]:
                endpoint_dict["request_body_serializer"] = body_param_dict[
                    "param_serializer"]
                imports_list.append(
                    body_param_dict["param_serializer_import_str"])
                endpoint_dict["request_body_serializer_is_array"] = \
                    body_param_dict["param_serializer_array"]

        for response_name, response in list(responses_dict.items()):
            response_name = response_name.replace("Status_", "")

            endpoint_dict["responses"][response_name] = {
                "response_serializer_sample_json": response["response_data"],
                "response_serializer": "None",
                "response_serializer_is_array": "False",
                "response_headers_serializer": "None",
                "response_headers_example_params": json.dumps(
                    response["response_headers_example_params"])
            }

            if response["response_serializer"]:
                endpoint_dict["responses"][response_name][
                    "response_serializer"] = response[
                    "response_serializer"]
                response_serializer_array = response[
                    "response_serializer_array"]
                if not response_serializer_array:
                    response_serializer_array = "False"
                endpoint_dict["responses"][response_name][
                    "response_serializer_is_array"] = \
                    response_serializer_array

                imports_list.append(response["response_serializer_import_str"])

            if response["response_headers_serializer"]:
                endpoint_dict["responses"][response_name][
                    "response_headers_serializer"] = response[
                    "response_headers_serializer"]
                imports_list.append(
                    response["response_headers_serializer_import_str"])

        endpoint_dict["imports_list"] = imports_list
        return endpoint_dict

    def get_all_parameters(self, method_name, parameter_type):

        parameters_list = self.get_parameters_list(parameter_type)

        method_parameters = self.get_method_parameters_list(method_name,
                                                            parameter_type)
        if parameter_type == 'body' and method_parameters:
            parameters_list = []

        for each_parameter in method_parameters:
            parameter_index = self.get_parameter_index(parameters_list,
                                                       each_parameter["name"])
            if parameter_index != -1:
                parameters_list[parameter_index] = each_parameter
            else:
                parameters_list.append(each_parameter)

        return parameters_list

    def generate_endpoint_file(self, endpoint_dict):
        operation_id = endpoint_dict["operation_id"]
        endpoint_file_content = self.get_endpoint_file_content(endpoint_dict)

        endpoint_file_path = \
            self.view_environment_path_dict()["view_environment_dir"] \
            + "/" + operation_id

        endpoint_file_path = endpoint_file_path + "/" + operation_id + ".py"

        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(endpoint_file_content, endpoint_file_path)

    @staticmethod
    def get_parameter_index(parameters_list, name):
        found_index = -1
        for index, each_parameter in enumerate(parameters_list):
            if each_parameter["name"] == str(name):
                return index
        return found_index

    def get_parameters_list(self, parameter_in):
        parameters_list = []
        parameters = self.path.get("parameters", [])  # each path's parameter
        for each_parameter in parameters:
            parameter_ref = each_parameter.get("$ref", None)
            if parameter_ref:
                each_parameter = self.get_parameter_from_ref(parameter_ref)
            if each_parameter["in"] == parameter_in:
                parameters_list.append(each_parameter)
        return parameters_list

    def get_method_parameters_list(self, request_method, parameter_in):
        parameters_list = []
        request_method_obj = self.path.get(request_method, None)
        if not request_method_obj:
            raise Exception("request method : %s not found" % request_method)
        else:
            parameters = request_method_obj.get("parameters", [])
            for each_parameter in parameters:
                parameter_ref = each_parameter.get("$ref", None)
                if parameter_ref:
                    each_parameter = self.get_parameter_from_ref(parameter_ref)
                if each_parameter["in"] == parameter_in:
                    parameters_list.append(each_parameter)
        return parameters_list

    def get_parameter_from_ref(self, parameter_ref):
        # available parameter used as $ref : #/parameters/<param_name>
        parameter_split = parameter_ref.split("#/parameters/")
        parameter_name = parameter_split[1]
        param_name = self.parser.parameters().get(parameter_name)
        self.check_for_validation(param_name['name'])

        return param_name

    def check_for_validation(self, param_name):
        # TODO add more invalid symbols in parameter name
        symbol = [' ', '-']
        for k in symbol:
            if k in param_name:
                if k == ' ':
                    print(
                        'Invalid Parameter name ::\"' + param_name + "\" \ncannot contain a white space")

                else:
                    print(
                        'Invalid Parameter name ' + param_name + "\ncannot contain a " + k)

                exit(1)

    def get_method_headers_dict(self, method_name, operation_id):
        all_headers_parameters = self.get_all_parameters(method_name,
                                                         "header")

        required_params = []
        optional_params = []
        params = {}
        example_params = {}

        for each_header in all_headers_parameters:

            from django_swagger_utils.drf_server.fields.header_parameter_field import \
                header_field
            header_param_properties = header_field(each_header)

            required = each_header.get("required", False)
            param_field_name = header_param_properties["param_field_name"]
            if required:
                required_params.append(param_field_name)
            else:
                optional_params.append(param_field_name)

            params[param_field_name] = {
                "field_string": header_param_properties[
                    "param_serializer_field"],

            }
            example_params[param_field_name] = {
                "param_example": header_param_properties["param_example"]
            }

        return self.request_header_serializer_dict(operation_id,
                                                   required_params,
                                                   optional_params, params,
                                                   example_params)

    def request_header_serializer_dict(self, operation_id, required_params,
                                       optional_params, params,
                                       example_params):

        serializer_dict = {
            "request_headers_serializer_import_str": "",
            "request_headers_serializer": None,
            "request_headers_params": {}
        }

        if params:
            from django_swagger_utils.core.utils.case_convertion import \
                to_camel_case
            camel_case_name = to_camel_case(operation_id)
            serializer_name = camel_case_name + "RequestHeaders"

            serializer_content = self.serializer_file_contents(
                required_params=required_params,
                optional_params=optional_params, params=params,
                object_params={}, serializer_name=serializer_name)

            file_path = self.view_environment_path_dict()[
                            "view_environment_dir"] + "/" + operation_id
            file_path = file_path + "/" + serializer_name + "Serializer.py"

            for param_name, param_props in list(example_params.items()):
                serializer_dict["request_headers_params"][param_name] = \
                    param_props["param_example"]

            from django_swagger_utils.core.utils.convert_path_to_package_str import \
                convert_path_to_package_str
            package_import_str = convert_path_to_package_str(file_path,
                                                             self.dir_paths[
                                                                 'base_dir'])

            from django_swagger_utils.core.utils.write_to_file import \
                write_to_file
            write_to_file(serializer_content, file_path)

            serializer_name += "Serializer"
            serializer_dict[
                "request_headers_serializer_import_str"] = "from %s import %s" % (
                package_import_str,
                serializer_name)
            serializer_dict["request_headers_serializer"] = serializer_name

        return serializer_dict

    def get_method_query_params_dict(self, method_name, operation_id):
        all_query_params_parameters = self.get_all_parameters(method_name,
                                                              "query")

        required_params = []
        optional_params = []
        params = {}

        for each_query in all_query_params_parameters:

            from django_swagger_utils.drf_server.fields.query_parameter_field import \
                query_param_field
            query_param_properties = query_param_field(each_query)

            required = each_query.get("required", False)
            param_field_name = query_param_properties["param_field_name"]
            if required:
                required_params.append(param_field_name)
            else:
                optional_params.append(param_field_name)

            params[param_field_name] = {
                "field_string": query_param_properties[
                    "param_serializer_field"],
                "param_example": query_param_properties["param_example"]
            }

        return self.request_query_param_serializer_dict(operation_id,
                                                        required_params,
                                                        optional_params,
                                                        params)

    def request_query_param_serializer_dict(self, operation_id,
                                            required_params, optional_params,
                                            params):

        serializer_dict = {
            "request_query_params_serializer_import_str": "",
            "request_query_params_serializer": None,
            "request_query_params": {}
        }

        if params:
            from django_swagger_utils.core.utils.case_convertion import \
                to_camel_case
            camel_case_name = to_camel_case(operation_id)
            serializer_name = camel_case_name + "RequestQueryParam"
            serializer_content = self.serializer_file_contents(
                required_params=required_params,
                optional_params=optional_params, params=params,
                object_params={}, serializer_name=serializer_name)

            for param_name, param_props in list(params.items()):
                serializer_dict["request_query_params"][param_name] = \
                    param_props["param_example"]

            file_path = self.view_environment_path_dict()[
                            "view_environment_dir"] + "/" + operation_id
            file_path = file_path + "/" + serializer_name + "Serializer.py"

            from django_swagger_utils.core.utils.convert_path_to_package_str import \
                convert_path_to_package_str
            package_import_str = convert_path_to_package_str(file_path,
                                                             self.dir_paths[
                                                                 'base_dir'])

            from django_swagger_utils.core.utils.write_to_file import \
                write_to_file
            write_to_file(serializer_content, file_path)

            serializer_name += "Serializer"
            serializer_dict[
                "request_query_params_serializer_import_str"] = "from %s import %s" % (
                package_import_str,
                serializer_name)
            serializer_dict[
                "request_query_params_serializer"] = serializer_name

        return serializer_dict

    def get_method_path_params_dict(self, method_name, operation_id):
        all_path_params_parameters = self.get_all_parameters(method_name,
                                                             "path")

        required_params = []
        optional_params = []
        params = {}

        for each_query in all_path_params_parameters:

            from django_swagger_utils.drf_server.fields.path_parameter_field import \
                path_param_field
            path_param_properties = path_param_field(each_query)

            required = each_query.get("required", False)
            param_field_name = path_param_properties["param_field_name"]
            if required:
                required_params.append(param_field_name)
            else:
                optional_params.append(param_field_name)

            params[param_field_name] = {
                "field_string": path_param_properties[
                    "param_serializer_field"],
                "param_example": path_param_properties["param_example"]
            }

        return self.request_path_param_serializer_dict(operation_id,
                                                       required_params,
                                                       optional_params,
                                                       params)

    def request_path_param_serializer_dict(self, operation_id,
                                           required_params, optional_params,
                                           params):

        serializer_dict = {
            "request_path_params_serializer_import_str": "",
            "request_path_params_serializer": None,
            "request_path_params": {}
        }

        if params:
            from django_swagger_utils.core.utils.case_convertion import \
                to_camel_case
            camel_case_name = to_camel_case(operation_id)
            serializer_name = camel_case_name + "RequestPathParam"
            serializer_content = self.serializer_file_contents(
                required_params=required_params,
                optional_params=optional_params, params=params,
                object_params={}, serializer_name=serializer_name)

            for param_name, param_props in list(params.items()):
                serializer_dict["request_path_params"][param_name] = \
                    param_props["param_example"]

            file_path = self.view_environment_path_dict()[
                            "view_environment_dir"] + "/" + operation_id
            file_path = file_path + "/" + serializer_name + "Serializer.py"

            from django_swagger_utils.core.utils.convert_path_to_package_str import \
                convert_path_to_package_str
            package_import_str = convert_path_to_package_str(file_path,
                                                             self.dir_paths[
                                                                 'base_dir'])

            from django_swagger_utils.core.utils.write_to_file import \
                write_to_file
            write_to_file(serializer_content, file_path)

            serializer_name += "Serializer"
            serializer_dict[
                "request_path_params_serializer_import_str"] = "from %s import %s" % (
                package_import_str,
                serializer_name)
            serializer_dict[
                "request_path_params_serializer"] = serializer_name

        return serializer_dict

    @staticmethod
    def serializer_file_contents(required_params, optional_params, params,
                                 object_params, serializer_name):

        serializer_context = {
            "required_params": required_params,
            "optional_params": optional_params,
            "params": params,
            "object_params": object_params,
            "serializer_camel_case_name": serializer_name
        }
        return render('serializers.j2', serializer_context)

    def get_property_dict(self, property_name, method_obj):
        global_property_dict = getattr(self.parser, property_name)()
        method_property_dict = method_obj.get(property_name, None)
        if method_property_dict is None:
            method_property_dict = global_property_dict
        return method_property_dict

    def get_method_body_parameter_dict(self, method_name, operation_id):
        body_param_properties = None
        all_body_parameters = self.get_all_parameters(method_name, "body")

        if all_body_parameters and len(all_body_parameters) != 1:
            raise Exception(
                "more than one body parameter found for operation: %s" % operation_id)

        if all_body_parameters:
            body_param = all_body_parameters[0]

            base_path = self.view_environment_path_dict()[
                            "view_environment_dir"] + "/" + operation_id

            from django_swagger_utils.drf_server.fields.body_field import \
                body_field
            body_param_properties = body_field(body_param, self.dir_paths,
                                               base_path,
                                               swagger_definitions=self.parser.definitions())

        return body_param_properties

    def get_responses_dict(self, method_obj):

        responses = method_obj.get("responses")
        operation_id = method_obj["operationId"]

        response_dict = {}
        response_methods = list(responses.keys())
        for response_code, response in list(responses.items()):
            response_code = "Status_" + response_code
            base_path = self.view_environment_path_dict()[
                            "view_environment_dir"] + "/" + operation_id
            base_path += "/responses/" + response_code

            from django_swagger_utils.drf_server.generators.response_generator import \
                ResponseGenerator
            response_generator = ResponseGenerator(self.dir_paths, response,
                                                   response_code,
                                                   self.parser.definitions(),
                                                   base_path,
                                                   self.parser.responses())
            if response_code == "default":
                from collections import defaultdict
                response_dict = defaultdict(
                    lambda: response_generator.generate_response_file(),
                    response_dict)
            else:
                response_dict[
                    response_code] = response_generator.generate_response_file()
        return response_dict

    @staticmethod
    def get_endpoint_file_content(endpoint_context):
        return render("endpoint.j2", endpoint_context)

    @staticmethod
    def get_mock_views_file_content(endpoint_context):
        return render('mock_view.j2', endpoint_context)

    def _get_mock_views_path(self, endpoint_dict):
        if self.group_name:
            mock_views_path = self.dir_paths["mock_views_dir"] + "/" + \
                              self.group_name + "/" + \
                              endpoint_dict["operation_id"]
        else:
            mock_views_path = self.dir_paths["mock_views_dir"] + "/" + \
                              endpoint_dict["operation_id"]

        return mock_views_path

    def _get_view_file_dir_path(self, endpoint_dict):
        if self.group_name:
            view_file_dir_path = \
                self.dir_paths["views_dir"] + "/" + self.group_name + "/" + \
                endpoint_dict["operation_id"] + "/"
        else:
            view_file_dir_path = \
                self.dir_paths["views_dir"] + "/" + \
                endpoint_dict["operation_id"] + "/"

        return view_file_dir_path

    def generate_view_flies(self, endpoint_dict):
        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists

        endpoint_dict.update({"app_name": self.app_name})
        mock_views_file_contents = self.get_mock_views_file_content(
            endpoint_dict)

        mock_views_path = self._get_mock_views_path(endpoint_dict)
        mock_views_file_path = \
            mock_views_path + "/" + endpoint_dict["operation_id"] + ".py"

        mock_view_api_wrapper_path = mock_views_path + "/api_wrapper.py"

        view_file_dir_path = self._get_view_file_dir_path(endpoint_dict)

        view_api_wrapper_path = view_file_dir_path + '/api_wrapper.py'
        api_wrapper_path_exists = check_path_exists(view_api_wrapper_path)

        view_file_path = view_file_dir_path + "/" + endpoint_dict[
            "operation_id"] + ".py"
        view_file_init_file_path = view_file_dir_path + "__init__.py"

        validator_class_path = view_file_dir_path + "validator_class.py"
        validator_class_path_exists = check_path_exists(validator_class_path)

        mock_view_validator_class_path = mock_views_path + "/validator_class.py"
        sample = view_file_dir_path + "request_response_mocks.py"

        # Delete existing files with name sample
        import subprocess
        subprocess.getoutput("rm " + view_file_dir_path + 'sample.txt')

        from django_swagger_utils.core.utils.write_to_file import write_to_file
        write_to_file(mock_views_file_contents, mock_views_file_path)

        context_dict = {
            'app_name': self.app_name,
            'operation_id': endpoint_dict['operation_id'],
            'group_name': self.group_name,
        }
        from django.conf import settings
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        from django_swagger_utils.drf_server.constants.enums import \
            CleanCodeViewsTestsVersion
        try:
            dsu_version = django_swagger_utils_settings['APPS'][
                self.app_name]['dsu_version']
        except KeyError:
            dsu_version = CleanCodeViewsTestsVersion.VERSION_ZERO.value

        if dsu_version == CleanCodeViewsTestsVersion.VERSION_ONE.value:
            context_dict['response_status_codes'] = list(
                endpoint_dict["responses"].keys())
            context_dict.update(self._get_mock_view_test_case_content(
                endpoint_dict))
            data = render('api_wrapper_template_v1.j2', context_dict)
        else:
            data = render('api_wrapper_template.j2', context_dict)
        if not api_wrapper_path_exists:
            write_to_file(data, view_api_wrapper_path)
        write_to_file(data, mock_view_api_wrapper_path)

        if not validator_class_path_exists:
            write_to_file(render('validator_class.j2', {}),
                          validator_class_path)
        write_to_file(render('validator_class.j2', {}),
                      mock_view_validator_class_path)

        is_view_file_exists = check_path_exists(view_file_path)

        if not is_view_file_exists:
            write_to_file(mock_views_file_contents, view_file_path)

        from django_swagger_utils.drf_server.utils.server_gen.get_api_environment import \
            get_api_environment, \
            check_to_execute_mock_test_for_operation
        view_init_file_contents = 'API_ENVIRONMENT = "%s"  # ENV_MOCK / ENV_IMPL\n' % \
                                  get_api_environment(
                                      self.app_name,
                                      endpoint_dict["operation_id"],
                                      group_name=self.group_name)

        view_init_file_contents = \
            view_init_file_contents + "EXECUTE_API_TEST_CASE = " + \
            str(check_to_execute_mock_test_for_operation(
                self.app_name, endpoint_dict["operation_id"],
                group_name=self.group_name)) + "\n"

        custom_scopes_check_func = getattr(
            settings, 'CUSTOM_SCOPES_CHECK_FUNCTION', None)

        if custom_scopes_check_func:
            view_init_file_contents = \
                view_init_file_contents + "CUSTOM_SCOPES = %s" % endpoint_dict[
                    "custom_scopes"]

        write_to_file(view_init_file_contents, view_file_init_file_path)

        sample_contents = self.generate_sample_json(endpoint_dict)
        write_to_file(sample_contents, sample)

    @staticmethod
    def _get_mock_view_test_case_content(endpoint_dict):
        try:
            body = json.loads(endpoint_dict["request_body_sample_json"])
        except ValueError:
            body = {}
        test_case = {
            "path_params": json.loads(
                str(endpoint_dict['default_request_path_params'])),
            "query_params": json.loads(str(
                endpoint_dict['request_query_params'])),
            "header_params": json.loads(str(
                endpoint_dict['request_headers_params'])),
            "securities": endpoint_dict["securities"],
            "body": body
        }
        return test_case

    def generate_sample_json(self, endpoint_context):
        return render('sample_json.j2', endpoint_context)

    def generate_new_testcase(self, req_operation_id, tcn, snapshot=False):
        found = False
        for method_name, each_method in list(self.path.items()):
            if method_name != "parameters" and each_method.get(
                'operationId') == req_operation_id:
                self.group_name = each_method.get('x-group', '')

                path_url, example_path_url, path_params_dict = self.get_method_path_url(
                    method_name)

                method_dict = {}
                operation_id = each_method["operationId"]
                request_method = method_name.upper()

                method_dict[request_method] = operation_id

                endpoint_dict = self.get_endpoint_dict(method_name,
                                                       each_method)
                endpoint_dict["path_params"] = json.dumps(path_params_dict)
                testing_url = self.clean_path_url(self.path_name)
                self.generate_test_cases(endpoint_dict, testing_url, tcn,
                                         snapshot=snapshot)
                found = True
                break

        return found

    def get_api_client_dict(self, req_operation_id):
        for method_name, each_method in list(self.path.items()):
            if method_name != "parameters" and each_method[
                'operationId'] == req_operation_id:
                path_url, example_path_url, path_params_dict = self.get_method_path_url(
                    method_name)
                endpoint_dict = self.get_endpoint_dict(method_name,
                                                       each_method)
                endpoint_dict["path_params"] = path_params_dict
                try:
                    endpoint_dict["request_body_dict"] = json.loads(
                        endpoint_dict["request_body_sample_json"])
                except ValueError:
                    endpoint_dict["request_body_dict"] = {}
                try:
                    if endpoint_dict["request_query_params"]:
                        endpoint_dict["request_query_params"] = json.loads(
                            endpoint_dict["request_query_params"])
                    else:
                        endpoint_dict["request_query_params"] = {}
                except ValueError:
                    endpoint_dict["request_query_params"] = {}
                try:
                    if endpoint_dict["request_headers_params"]:
                        endpoint_dict["request_headers_params"] = json.loads(
                            endpoint_dict["request_headers_params"])
                    else:
                        endpoint_dict["request_headers_params"] = {}
                except ValueError:
                    endpoint_dict["request_headers_params"] = {}
                if isinstance(
                    endpoint_dict["request_body_serializer_is_array"], str):
                    endpoint_dict["request_body_serializer_is_array"] = eval(
                        endpoint_dict["request_body_serializer_is_array"])
                return endpoint_dict

    def _get_tests_dir_path_for_dsu_version_one(self, endpoint_dict):
        if self.group_name:
            tests_dir_path = \
                self.dir_paths["tests_dir"] + "/views/" + self.group_name + \
                "/" + endpoint_dict["operation_id"] + "/"
        else:
            tests_dir_path = self.dir_paths["tests_dir"] + "/views/" + \
                             endpoint_dict["operation_id"] + "/"
        return tests_dir_path

    def _get_tests_dir_path_for_dsu_version_zero(self, endpoint_dict):
        if self.group_name:
            tests_dir_path = \
                self.dir_paths["views_dir"] + "/" + self.group_name + "/" + \
                endpoint_dict["operation_id"] + "/tests/"
        else:
            tests_dir_path = self.dir_paths["views_dir"] + "/" + endpoint_dict[
                "operation_id"] + "/tests/"
        return tests_dir_path

    def generate_test_cases(self, endpoint_dict, example_path_url, tcn,
                            snapshot=False):
        from django_swagger_utils.core.utils.write_to_file import write_to_file
        from django.conf import settings
        from django_swagger_utils.drf_server.constants.enums import \
            CleanCodeViewsTestsVersion
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        try:
            dsu_version = django_swagger_utils_settings['APPS'][
                self.app_name]['dsu_version']
        except KeyError:
            dsu_version = CleanCodeViewsTestsVersion.VERSION_ZERO.value

        if dsu_version == CleanCodeViewsTestsVersion.VERSION_ONE.value:
            tests_dir_path = self._get_tests_dir_path_for_dsu_version_one(
                endpoint_dict)
        else:
            tests_dir_path = self._get_tests_dir_path_for_dsu_version_zero(
                endpoint_dict)

        sample_test_case = "test_case_{0}.py".format(str(tcn).zfill(2))
        sample_test_case_path = tests_dir_path + sample_test_case

        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists
        is_test_case_file_exists = check_path_exists(sample_test_case_path)

        endpoint_dict["securities"] = self.get_test_case_security_dict(
            endpoint_dict["securities"])
        if not is_test_case_file_exists:
            from django_swagger_utils.core.utils.case_convertion import \
                to_camel_case
            camel_case_operation_name = to_camel_case(
                endpoint_dict["operation_id"])
            sample_test_case = sample_test_case.split(".")[0]
            endpoint_dict["test_case_class"] = to_camel_case(
                sample_test_case) + camel_case_operation_name \
                                               + "APITestCase"
            if snapshot:
                sample_test_case_contents = self.get_snapshot_test_content(
                    endpoint_dict, dsu_version)
            else:
                sample_test_case_contents = self.get_tests_file_contents(
                    endpoint_dict)

            from yapf.yapflib.yapf_api import FormatCode
            formatted_test_case_contents = \
                FormatCode(sample_test_case_contents)
            write_to_file(formatted_test_case_contents[0],
                          sample_test_case_path)

        from django_swagger_utils.drf_server.utils.server_gen.get_test_cases_dict import \
            get_test_cases_dict

        if dsu_version == CleanCodeViewsTestsVersion.VERSION_ZERO.value:
            test_cases_dict = get_test_cases_dict(
                tests_dir_path,
                endpoint_dict["operation_id"]
            )
            endpoint_dict["test_cases"] = test_cases_dict
        endpoint_dict["example_path_url"] = example_path_url

        tests_init_file = tests_dir_path + "__init__.py"
        tests_init_file_contents = self.get_tests_init_file_contents(
            endpoint_dict)

        write_to_file(tests_init_file_contents, tests_init_file)

    @staticmethod
    def get_tests_file_contents(endpoint_context):
        return render('test_case.j2', endpoint_context)

    def get_snapshot_test_content(self, endpoint_context, dsu_version):
        from django_swagger_utils.drf_server.constants.enums import \
            CleanCodeViewsTestsVersion
        securities = json.loads(endpoint_context["securities"])
        if dsu_version == CleanCodeViewsTestsVersion.VERSION_ONE.value:
            try:
                body = json.loads(endpoint_context['request_body_sample_json'])
            except ValueError:
                body = {}
            endpoint_context.update({
                'securities': str(self.get_securities_for_snapshot_file(securities)),
                'request_query_params': json.loads(
                    str(endpoint_context['request_query_params'])),
                'path_prams': json.loads(
                    str(endpoint_context['default_request_path_params'])),
                'request_headers_params': json.loads(
                    str(endpoint_context['request_headers_params'])),
                'body': body
            })
            return render('snapshot_test_v1.j2', endpoint_context)
        else:
            return render('snapshot_test.j2', endpoint_context)

    @staticmethod
    def get_securities_for_snapshot_file(securities):
        if not "oauth" in securities:
            return {}
        if securities["oauth"]["type"] == "oauth2":
            oauth_type = "oauth"
        else:
            oauth_type = securities["oauth"]["type"]
        scopes = securities["oauth"]["scopes"]
        return {oauth_type: {'scopes': scopes}}

    @staticmethod
    def get_tests_init_file_contents(endpoint_context):
        return render('test_case_init_file.j2', endpoint_context)

    def get_test_case_security_dict(self, securities):
        security_defs = self.parser.security_definitions()
        new_security = {}
        for each_security in securities:
            if each_security:
                security_name = list(each_security.keys())[0]
                security_def = security_defs.get(security_name, {})
                # currently supporting only oauth2 security in test_cases
                if security_def:
                    if security_def.get("type") == "oauth2":
                        security_def.update(
                            {"scopes": each_security[security_name]})
                        new_security[security_name] = security_def
                    elif security_def.get("type") == "apiKey":
                        security_key_name = security_def.get("name")
                        security_def.update({"value": "api_key",
                                             "header_name": "HTTP_" + security_key_name.upper().replace(
                                                 "-", "_")})
                        new_security[security_name] = security_def
                    elif security_def.get("type") == "basic":
                        security_def.update(
                            {"username": "username", "password": "password"})
                        new_security[security_name] = security_def
        return json.dumps(new_security)
