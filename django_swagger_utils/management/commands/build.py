import json
import os
import shutil
import subprocess
from io import open

from django.core.management.base import BaseCommand, CommandError


class Build(object):
    spec_json = None
    parser = None
    paths = dict()

    def __init__(self, app_name, base_dir, settings=None,
                 is_validation_required=True):
        self.app_name = app_name
        self.base_dir = base_dir
        self.settings = settings
        self.initiate_build(is_validation_required)

    def initiate_build(self, is_validation_required=True):
        # setup build specific paths
        self.setup_paths()

        # create settings file if not exists
        self.check_create_settings_file()

        # step1 check build dir exists
        # self.check_build_exists()

        # step3 validate specs_json
        if is_validation_required:
            # step2 load api_spec.json into spec_json
            self.load_spec_file(self.paths["api_specs_json"])

            self.validate_swagger()

        # step4 custom spec validation
        self.custom_spec_validator()

        # step5 parser swagger specs
        self.parse_swagger_specs()

    def setup_paths(self):
        """
        defines paths used in the project
        :return:
        """
        # TODO: separate out paths based on android, json patch, server_gen.
        app_base_path = os.path.join(self.base_dir, self.app_name)
        build_dir = os.path.join(app_base_path, "build")
        api_spec_dir = os.path.join(app_base_path, "api_specs")
        api_spec_migrations_dir = os.path.join(api_spec_dir, "migrations")
        api_specs_json = os.path.join(api_spec_dir, "api_spec.json")
        request_response_dir = os.path.join(build_dir, "request_response")
        decorator_options_file = os.path.join(request_response_dir,
                                              "decorator_options.py")
        security_definitions_file = os.path.join(request_response_dir,
                                                 "security_definitions.py")
        serializers_base_dir = os.path.join(build_dir, "serializers")
        definitions_serializers_base_dir = os.path.join(serializers_base_dir,
                                                        "definitions")
        global_parameters_dir = os.path.join(build_dir, "parameters")
        global_response_dir = os.path.join(build_dir, "responses")
        url_file = os.path.join(build_dir, "urls.py")
        mobx_base_dir = os.path.join(build_dir, "mobx_classes")
        mobx_base_dir_models = os.path.join(mobx_base_dir, 'models')
        mobx_base_dir_responses = os.path.join(mobx_base_dir, 'responses')
        mobx_base_dir_endpoints = os.path.join(mobx_base_dir, 'endpoints')
        mobx_base_dir_parameters = os.path.join(mobx_base_dir, 'parameters')
        view_environments_dir = os.path.join(build_dir, "view_environments")
        sample_json_dir = os.path.join(app_base_path, "conf", "responses")
        settings_file = os.path.join(app_base_path, "conf", "settings.py")
        mock_views_dir = os.path.join(build_dir, "mock_views")
        views_dir = os.path.join(app_base_path, "views")
        api_environment_file = os.path.join(api_spec_dir, "api_environment.py")
        android_base_dir = os.path.join(build_dir,
                                        "android_%s" % self.app_name)
        api_doc_dir = os.path.join(build_dir, "docs")
        tests_dir = os.path.join(app_base_path, "tests")
        global_jars_dir = os.path.join(self.base_dir, "android_jars")
        zappa_settings = os.path.join(self.base_dir, "zappa_settings.json")
        apidoc = os.path.join(self.base_dir, "apidoc.json")
        docs = os.path.join(self.base_dir, "docs")
        static = os.path.join(self.base_dir, "static")
        static_docs = os.path.join(static, "docs")
        interface_dir = os.path.join(app_base_path, 'interfaces')
        service_interface_path = os.path.join(interface_dir, self.app_name
                                              + '_service_interface.py')
        client_app_base_path = app_base_path + "_client"
        client_interface_path = os.path.join(client_app_base_path,
                                             'interface.py')
        client_api_client_path = os.path.join(client_app_base_path,
                                              'api_client.py')
        client_constants_path = os.path.join(client_app_base_path,
                                             'constants.py')
        client_app_init_file = os.path.join(client_app_base_path, '__init__.py')
        base_app_init_file = os.path.join(app_base_path, '__init__.py')

        client_setup_py_path = os.path.join(self.base_dir, "setup.py")
        client_manifest_path = os.path.join(self.base_dir, "MANIFEST.in")
        client_app_base_path_egg_info = client_app_base_path + ".egg-info"
        pypi_dist_path = os.path.join(self.base_dir, "dist")
        package_json = os.path.join(self.base_dir, "package.json")
        docs_html_dir = os.path.join(app_base_path, "docs_html")
        md_file_name = os.path.join(docs_html_dir, "docs.md")
        utils_dir = os.path.join(app_base_path, "constants")
        const_file_name = os.path.join(utils_dir, "generated_enums.py")
        self.paths = {
            "base_dir": self.base_dir,
            "app_base_path": app_base_path,
            "build_dir": build_dir,
            "api_spec_dir": api_spec_dir,
            "api_spec_migrations_dir": api_spec_migrations_dir,
            "api_specs_json": api_specs_json,
            "request_response_dir": request_response_dir,
            "decorator_options_file": decorator_options_file,
            "security_definitions_file": security_definitions_file,
            "serializers_base_dir": serializers_base_dir,
            "definitions_serializers_base_dir": definitions_serializers_base_dir,
            "global_parameters_dir": global_parameters_dir,
            "global_response_dir": global_response_dir,
            "url_file": url_file,
            "view_environments_dir": view_environments_dir,
            "sample_json_dir": sample_json_dir,
            "settings_file": settings_file,
            "mock_views_dir": mock_views_dir,
            "views_dir": views_dir,
            "api_environment_file": api_environment_file,
            "android_base_dir": android_base_dir,
            "api_doc_dir": api_doc_dir,
            "tests_dir": tests_dir,
            "global_jars_dir": global_jars_dir,
            "zappa_settings": zappa_settings,
            "apidoc": apidoc,
            "static": static,
            "static_docs": static_docs,
            "docs": docs,
            "interface_dir": interface_dir,
            "service_interface_path": service_interface_path,
            "client_app_base_path": client_app_base_path,
            "client_interface_path": client_interface_path,
            "client_api_client_path": client_api_client_path,
            "client_setup_py_path": client_setup_py_path,
            "client_app_base_path_egg_info": client_app_base_path_egg_info,
            "client_manifest_path": client_manifest_path,
            "client_app_init_file": client_app_init_file,
            "client_constants_path": client_constants_path,
            "base_app_init_file": base_app_init_file,
            "pypi_dist_path": pypi_dist_path,
            "mobx_base_dir": mobx_base_dir,
            'mobx_base_dir_models': mobx_base_dir_models,
            'mobx_base_dir_responses': mobx_base_dir_responses,
            'mobx_base_dir_endpoints': mobx_base_dir_endpoints,
            'mobx_base_dir_parameters': mobx_base_dir_parameters,
            "package_json": package_json,
            "docs_html_dir": docs_html_dir,
            "md_file_name": md_file_name,
            "const_file_name": const_file_name
        }

    def create_package_json(self):
        """
        creates package_json.json file
        :return:
        """
        f = open(self.paths["package_json"], "w")
        from django_swagger_utils.spec_client.get_package_json import \
            package_json
        f.write(package_json)
        f.close()

    def delete_package_json(self):
        """
        deletes package_json file
        :return:
        """
        os.remove(self.paths["package_json"])

    def install_for_spec(self):
        """
        necessary packages for splitting and merging , 3rd package will be called only if splitting is taking place,
        hence will be installed only during splitting process
        :return:
        """
        self.create_package_json()
        os.system('npm install json-refs')
        os.system('npm install json2yaml')
        os.system('npm install yamljs')
        os.system(
            'npm install swagger-split')  # package only required while splitting hence being installed here
        self.delete_package_json()

    def merge_spec(self):
        """
        Merges the spec file if the api_spec folder cotains the spec folder which further contains the spec file as small parts
        divided into directories
        :return:
        """
        from django_swagger_utils.spec_client.merge_spec import MergeSpec
        merge_spec = MergeSpec(self.paths['api_spec_dir'],
                               self.paths['base_dir'])
        merge_spec.merge()

    def split_spec(self):
        """
        splits the present api_spec.json into further spec folder divided into smaller bits
        :return:
        """
        from django_swagger_utils.spec_client.split_spec import SplitSpec
        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists

        if check_path_exists(
            os.path.join(self.paths['api_spec_dir'], "specs")):
            from shutil import rmtree
            rmtree(os.path.join(self.paths['api_spec_dir'], "specs"))
        split_spec = SplitSpec(self.paths['api_spec_dir'],
                               self.paths['base_dir'])
        split_spec.split()

    def generate_spec_from_sgui(self):

        """
        gets the configuration from settings
        verifies the app by checking in swagger apps
        if app is verified, generates build based on the spec file from server

        :return:
        """
        from django.conf import settings

        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = django_swagger_utils_settings['APPS']
        app_settings = swagger_apps[self.app_name]

        config_list = self.parse_swagger_gui_config(app_settings)

        if not config_list:
            return
        access_token = config_list[0]
        organization_id = config_list[1]
        project_id = config_list[2]
        app_id = config_list[3]
        base_url = config_list[4]
        from django_swagger_utils.swagger_gui.swagger_spec import SwaggerSpec
        swagger_spec = SwaggerSpec(access_token, organization_id, project_id,
                                   app_id, base_url, self.paths)
        is_app = swagger_spec.verify_app()
        if is_app:
            spec_file = swagger_spec.get_spec_file()
            self.spec_json = spec_file
            self.parse_swagger_specs()
            self.generate_specs_build()
        return

    def parse_swagger_gui_config(self, app_settings):
        """
        {
            "SWAGGER_GUI_CONFIG":{
                "ACCESS_TOKEN":"",
                "ORGANIZATION_ID":1,
                "PROJECT_ID":1,
                "APP_ID":1,
                "SERVICE_URL":""
            }
        }
        :param app_settings:
        :return: [access_token, organization_id, project_id, app_id, base_url]
        """
        sgui_config = app_settings.get('SWAGGER_GUI_CONFIG')
        from colored import fg, attr

        if not sgui_config:
            print('{}{}{}SGUI_CONFIG not found in settings. Please define the '
                  'configuration!'.format(fg(1), attr(1), attr(4)))
            return None

        access_token = sgui_config.get('ACCESS_TOKEN')
        if not access_token:
            print(
                '{}{}{}ACCESS_TOKEN not found in SWAGGER_GUI_CONFIG. Please '
                'define the configuration!'.format(fg(1), attr(1), attr(4)))
            return None

        organization_id = sgui_config.get('ORGANIZATION_ID')
        if not organization_id:
            print(
                '{}{}{}ORGANIZATION_ID not found in SWAGGER_GUI_CONFIG. '
                'Please define the configuration!'.format(
                    fg(1), attr(1), attr(4)))
            return None

        project_id = sgui_config.get('PROJECT_ID')
        if not project_id:
            print(
                '{}{}{}PROJECT_ID not found in SWAGGER_GUI_CONFIG. Please define '
                'the configuration!'.format(fg(1), attr(1), attr(4)))
            return None

        app_id = sgui_config.get('APP_ID')
        if not app_id:
            print(
                '{}{}{}APP_ID not found in SWAGGER_GUI_CONFIG. Please define '
                'the configuration!'.format(fg(1), attr(1), attr(4)))
            return None

        base_url = sgui_config.get('SERVICE_URL')
        if not base_url:
            print(
                '{}{}{}SERVICE_URL not found in SWAGGER_GUI_CONFIG. '
                'Please define the configuration!'.format(
                    fg(1), attr(1), attr(4)))
            return None

        return [access_token, organization_id, project_id, app_id, base_url]

    def sync_spec_from_sgui(self):
        """
        parse the swagger gui config
        verify the app using organization id and project id
        update the current project's spec file using server based spec file
        :return:
        """
        from django.conf import settings

        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = django_swagger_utils_settings['APPS']
        app_settings = swagger_apps[self.app_name]
        config_list = self.parse_swagger_gui_config(app_settings)

        if not config_list:
            return
        access_token = config_list[0]
        organization_id = config_list[1]
        project_id = config_list[2]
        app_id = config_list[3]
        base_url = config_list[4]
        from django_swagger_utils.swagger_gui.swagger_spec import SwaggerSpec
        swagger_spec = SwaggerSpec(access_token, organization_id, project_id,
                                   app_id, base_url, self.paths)
        is_app = swagger_spec.verify_app()
        if is_app:
            swagger_spec.sync_spec_file()
        return

    def create_mobx_from_templates(self):
        '''
        This method will create a MobxTemplateGenerator object , which will be helpful to generate
        definitions , responses and endpoints.
        :return:
        '''

        from django_swagger_utils.mobx_client.mobx_client import \
            MobxTemplateGenerator
        mobxtemplategenerator = MobxTemplateGenerator(self.parser,
                                                      self.app_name,
                                                      self.paths[
                                                          'mobx_base_dir'],
                                                      self.paths)
        mobxtemplategenerator.generate_definitions(
            self.paths['mobx_base_dir_models'])
        mobxtemplategenerator.generate_responses(
            self.paths['mobx_base_dir_responses'])
        mobxtemplategenerator.generate_endpoints(
            self.paths['mobx_base_dir_endpoints'])
        mobxtemplategenerator.generate_parameters(
            self.paths['mobx_base_dir_parameters'])

    def add_to_npm(self):
        '''
        Credentials to jfrog are needed to upload the mobx classes as npm package. credentials need to be uploaded
        in ~/.npmrc file.
        :return:
        '''
        self.generate_apidoc_patches()
        vnum = self.get_version()

        from django_swagger_utils.mobx_client.mobx_npm_deployment import \
            MobxNpmDeployment
        mobnpmdeployment = MobxNpmDeployment(self.app_name, self.paths, vnum)
        mobnpmdeployment.delete_previous()
        mobnpmdeployment.create_template()
        mobnpmdeployment.compress_to_npm()
        mobnpmdeployment.delete_previous()

    def check_create_settings_file(self):
        """
        checks if settings file is present else writes app name to settings file
        :return:
        """
        path = self.paths["settings_file"]
        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists
        settings_file = check_path_exists(path)
        if not settings_file:
            settings_file_contents = "# '%s' settings" % self.app_name
            from django_swagger_utils.core.utils.write_to_file import \
                write_to_file
            write_to_file(settings_file_contents, path)

    def check_build_exists(self):
        """
        checks if build folder exists
        :return:
        """
        path = self.base_dir + "/" + self.app_name + "/" + "build"
        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists
        build_dir = check_path_exists(path)
        if build_dir:
            raise Exception(
                "Build Directory Already Exist, please run update_specs_build")

    def generate_interfaces(self, override):
        """
        class for Interface Generation and also to generate sample request and response.
        :return:
        """
        from django_swagger_utils.interface_client.interface_generator import \
            InterfaceGenerator
        interface_generator = InterfaceGenerator(self.app_name, self.parser,
                                                 self.paths, override)
        interface_generator.generate_interfaces()

    def load_spec_file(self, spec_file):
        """
            forms a dict from json and raises exception if not present
        :param spec_file:
        :return:
        """
        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists
        spec_file_path = check_path_exists(spec_file)
        # print spec_file_path, spec_file,  self.app_name
        if not spec_file_path:
            raise Exception("%s missing" % spec_file)
        with open(spec_file) as f:
            json_text = f.read()
            try:
                self.spec_json = json.loads(json_text)
            except ValueError:
                print("The \"%s/api_specs/api_spec.json\" is not a proper JSON." % self.app_name)
                exit(1)

    def validate_swagger(self):
        from swagger_spec_validator.util import get_validator
        validator = get_validator(self.spec_json)
        validator.validate_spec(self.spec_json, spec_url='')

    def custom_spec_validator(self):
        # todo need to check for unsupported features present in the specs_json

        # content-type "application/json", "application/x-www-form-urlencoded", -- multipart/form-data not supported
        # parameter type "formData" not supported
        # custom header parameter name does not match standard http request / response headers
        # path parameters regex must be single group
        # file - parameter types not supported
        # path param value must be single word, no spaces allowed in param name
        # python keywords as key / properties names
        # allOff not supported yet
        # response headers - to _ convertion, naming convertion
        # not allowing 'default' key as response method
        self._validate_group_names_and_operation_ids()
        pass

    def _validate_group_names_and_operation_ids(self):
        paths = self.spec_json['paths']

        operation_ids = list()
        group_names = list()
        for path, path_dict in paths.items():
            for method, method_dict in path_dict.items():
                if method in ["get", "put", "post", "delete", "options",
                              "head", "patch"]:
                    operation_ids.append(method_dict['operationId'])
                    if method_dict.get('x-group', ''):
                        group_names.append(method_dict['x-group'])

        from django_swagger_utils.drf_server.exceptions import BadRequest
        for group_name in group_names:
            for operation_id in operation_ids:
                if group_name == operation_id:
                    raise BadRequest(
                        "group name and operation_id can not be same")

    def parse_swagger_specs(self):
        from django_swagger_utils.core.parsers.swagger_parser import \
            SwaggerParser
        self.parser = SwaggerParser(spec_json=self.spec_json)

    def generate_apidoc_patches(self):
        """
        generates patches for changes in spec
        :return:
        """
        base_path = self.paths["api_doc_dir"]
        from django_swagger_utils.core.utils.mk_dirs import MkDirs
        MkDirs().mk_dir_if_not_exits(file_name=base_path + "/")

        from django_swagger_utils.apidoc_gen.generators.patch_generator import \
            PatchGenerator

        patch_generator = PatchGenerator(self.app_name, self.parser,
                                         self.paths, base_path)
        # generating api docs
        patch_generator.generate_json_patch()

    def get_version(self):
        """
        :return: the version of spec file
        """
        import os
        version = 0
        if os.path.exists(self.paths["api_spec_migrations_dir"]):
            version_list = []
            dir_list = os.listdir(self.paths["api_spec_migrations_dir"])
            for dl in dir_list:
                if '_patch.json' in dl:
                    version_num = int(dl.replace("_patch.json", ""))
                    version_list.append(version_num)
            version_list.sort(reverse=False)
            if len(version_list) != 0:
                version = version_list[-1]
        version += 1
        return version

    def generate_patch_build(self, domain):
        # TODO change name of def
        """
        generates docs for patches
        :param domain:
        :return:
        """
        base_path = self.paths["api_doc_dir"]
        self.generate_apidoc_patches()
        from django_swagger_utils.apidoc_gen.generators.patch_generator import \
            PatchGenerator
        patch_generator = PatchGenerator(self.app_name, self.parser,
                                         self.paths, base_path)
        patch_generator.filter_for_deleted_apis()

        process = subprocess.Popen(['which', 'apidoc'], stdout=subprocess.PIPE)

        output = process.communicate()[0]
        if output:

            apidoc_json_path = os.path.join(self.paths["base_dir"], "apidoc.json")
            if not os.path.exists(apidoc_json_path):
                with open(apidoc_json_path, 'w') as outfile:
                    apidoc_content = {
                        "url": "https://ib-backend-dev.apigateway.in",
                        "version": "0.0.1",
                        "description": "",
                        "name": "iBHubs_backend API Documentation",
                        "title": "iBHubs_backend Documentation"}
                    json.dump(apidoc_content, outfile, indent=4)
            # by default we assume user is working at no specific branch so we fix
            # url to default above url as above , then we check if any specific parametr is given
            # and replace url with required url
            if domain != '' and domain:
                with open(self.paths["apidoc"]) as src_json:
                    apidoc_content = json.load(src_json)
                    apidoc_content['url'] = "https://" + domain
                with open(self.paths["apidoc"], 'w') as outfile:
                    json.dump(apidoc_content, outfile, indent=2)
            # the below command is responsible for creating docs

            output_path = os.path.join(self.base_dir, 'docs_{}'.format(self.app_name))
            destination_path = os.path.join(self.base_dir, 'docs', self.app_name)

            api_doc_options = ['apidoc', '-i', os.path.join(self.base_dir, self.app_name, 'build', 'docs'),
                               '-o',
                               output_path,
                               '-e', 'django_swagger_utils/*',
                               '-e', 'static/*',
                               '-e', 'node_modules/*']
            from django.conf import settings
            api_doc_exclude_dirs = getattr(settings,
                                           'API_DOC_EXCLUDE_DIRS', [])
            if api_doc_exclude_dirs:
                for each_dir in api_doc_exclude_dirs:
                    api_doc_options.extend(['-e', "{}/*".format(each_dir)])
            process = subprocess.Popen(api_doc_options, stdout=subprocess.PIPE)
            print(process.communicate()[0])
            shutil.move(output_path, destination_path)
            ################################################
            # hosting apidoc
            ################################################
            # obtaining the path of static folder of django-swagger-utils
            # django_swagger_utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            # static_folder_path = os.path.join(django_swagger_utils_path, "static")
            # import shutil
            # # create a folder apidoc , delete if previously exists
            # if os.path.exists(os.path.join(static_folder_path, "apidoc")):
            #     shutil.rmtree(os.path.join(static_folder_path, "apidoc"))
            # apidoc_path = os.path.join(static_folder_path, "apidoc")
            #
            # os.mkdir(apidoc_path)

            # from distutils.dir_util import copy_tree
            # copydocs from docs to apidoc in swagger utils
            # try:
            #     copy_tree(os.path.join(self.base_dir, 'docs'), apidoc_path)
            # except Exception as err:
            #     print err

            # browse to localhost:<port>/static/apidoc/index.html

        else:
            raise CommandError(
                "Help: Install apidoc: [ sudo npm install -g apidoc ]")

    def generate_specs_build(self):
        """
        generates the elements present in spec file
        :return:
        """
        from django_swagger_utils.drf_server.generators.swagger_generator import \
            SwaggerGenerator

        swagger_gen = SwaggerGenerator(self.parser, self.paths, self.app_name)
        # generating request_response files
        swagger_gen.generate_request_response()
        # testing properties
        swagger_gen.generate_definitions()
        # generating global parameters
        swagger_gen.generate_parameters()
        # generating global response
        swagger_gen.generate_responses()
        # generating urls
        swagger_gen.generate_urls()

    def create_documentation(self, app, counter):
        """
        documentation of the spec file - creates a .md file
        """
        from django_swagger_utils.core.utils.write_to_file import write_to_file
        from django_swagger_utils.apidoc_gen.generators.markdown_generator import \
            MarkdownGenerator

        filename = self.paths["md_file_name"]

        a = ""
        if counter == 0:
            a += "# " + "DOCUMENTATION" + "\n\n"
            counter += 1

        a += "## " + app.title() + "  APIs" + "\n" + "------" + "\n\n"
        write_to_file(a, filename, init_required=False)

        base_path = os.path.join(self.base_dir, self.app_name)
        markdown_obj = MarkdownGenerator(self.app_name, self.parser,
                                         self.paths, base_path)
        filepath = markdown_obj.create_documentation(filename)
        # markdown_obj.convert_to_html(filepath)

    def constant_gen(self, override):
        """
        creates the constants(.py) file for the variables in the spec file
        """
        from django_swagger_utils.core.utils.check_path_exists import \
            check_path_exists
        from django_swagger_utils.core.utils.write_to_file import write_to_file
        from django_swagger_utils.apidoc_gen.generators.constant_generator_v2 import \
            ConstantGeneratorV2

        file_name = self.paths["const_file_name"]
        file_exists = check_path_exists(file_name)

        # create the folder and file if either of them doesn't exist
        if not file_exists:
            write_to_file("", file_name)

        # if the file already exists and override command are not given
        if file_exists and not override:
            print("can't perform the action as file already exists in the " + self.app_name + " app")

        # if the file doesn't exist or override command is given
        if not file_exists or override:
            constant_obj = ConstantGeneratorV2(self.parser, file_name)
            constant_obj.constant_gen()

    def android_build(self):
        """
        generate and deploys jar file
        firstfind thelates evrsion number following which generate jar and deploy it
        :return:
        """

        self.generate_apidoc_patches()
        vnum = self.get_version()
        self.android_jar_genaration(vnum)
        self.android_jar_deployment(vnum)

    def android_jar_genaration(self, vnum):
        """
        generates jar
        :param vnum: version number
        :return:
        """
        base_path = self.paths["android_base_dir"]
        from django_swagger_utils.android_client.generators.android_generator import \
            AndroidGenerator
        android_gen = AndroidGenerator(self.app_name, self.parser, self.paths,
                                       base_path)

        # generating all android models
        android_gen.generate_all_models()

        # generating android requests
        android_gen.generate_android_requests_responses()

        # generating android server_gen commands
        android_gen.generate_android_server_commands()

        # generating jar files
        android_gen.generate_jars(vnum)

    def android_jar_deployment(self, vnum):
        """
        deploys the jar in the remote artifactory
        :param vnum: version number
        :return:
        """
        from django_swagger_utils.android_client.generators.android_deployment import \
            AndroidJarDeployment
        base_path = self.paths["android_base_dir"]
        android_deploy = AndroidJarDeployment(self.app_name, self.parser,
                                              self.paths, base_path)
        android_deploy.jar_deployment(vnum)

    def android_build_v2(self):
        """
       generate and deploys jar file for version 2
       firstfind thelates evrsion number following which generate jar and deploy it
       :return:
       """
        self.generate_apidoc_patches()
        vnum = self.get_version()
        self.android_jar_v2_genaration(vnum)
        self.android_jar_v2_deployment(vnum)

    def android_jar_v2_genaration(self, vnum):
        """
        generates the jar for the spec
        :param vnum: version number
        :return:
        """
        base_path = self.paths["android_base_dir"]
        from django_swagger_utils.android_client_v2.generators_v2.android_generator_v2 import \
            AndroidGeneratorV2
        android_gen = AndroidGeneratorV2(self.app_name, self.parser,
                                         self.paths, base_path)

        # generating all android models
        android_gen.generate_all_models_v2()

        # generating android requests
        android_gen.generate_android_requests_responses_v2()

        # generating android server_gen commands
        android_gen.generate_android_server_commands_v2()

        # generating jar files
        android_gen.generate_jars_v2(vnum)

    def android_jar_v2_deployment(self, vnum):
        """
        deploys the jar in remote artifactory
        :param vnum: version number
        :return:
        """
        base_path = self.paths["android_base_dir"]
        from django_swagger_utils.android_client_v2.generators_v2.android_deployment_v2 import \
            AndroidJarDeploymentV2
        android_deploy = AndroidJarDeploymentV2(self.app_name, self.parser,
                                                self.paths, base_path)
        android_deploy.jar_deployment_v2(vnum)

    def clean(self):
        """
        deletes the build and docs
        :return:
        """
        if os.path.exists(self.paths['build_dir']):
            shutil.rmtree(self.paths['build_dir'])
        if os.path.exists(os.path.join(self.base_dir, 'docs')):
            shutil.rmtree(os.path.join(self.base_dir, 'docs'))
        os.system("find . -name \*.pyc -delete")

    def clean_docs(self):
        """
        deletes only docs related folders
        :return:
        """
        if os.path.exists(self.paths['api_doc_dir']):
            shutil.rmtree(self.paths['api_doc_dir'])
        print(os.path.join(self.paths['docs'], self.app_name), self.paths['api_doc_dir'])
        if os.path.exists(os.path.join(self.paths['docs'], self.app_name)):
            shutil.rmtree(os.path.join(self.paths['docs'], self.app_name))
        os.system("find . -name \*.pyc -delete")

    @property
    def swagger_generator(self):
        from django_swagger_utils.drf_server.generators.swagger_generator import \
            SwaggerGenerator
        swagger_gen = SwaggerGenerator(self.parser, self.paths, self.app_name)
        return swagger_gen

    def generate_api_client_interface(self):

        from django_swagger_utils.interface_client.interface_generator import \
            InterfaceGenerator
        interface_generator = InterfaceGenerator(self.app_name, self.parser,
                                                 self.paths, True)
        interface_generator.generate_interfaces(
            self.paths["client_interface_path"])

    def generate_api_client_constants(self):

        from django_swagger_utils.apidoc_gen.generators.constant_generator_v2 \
            import ConstantGeneratorV2
        constant_obj = ConstantGeneratorV2(self.parser,
                                           self.paths["client_constants_path"])
        constant_obj.constant_gen()

    def generate_api_client(self):
        from django_swagger_utils.api_client.api_client_generator import \
            APIClientGenerator
        api_client_generator = APIClientGenerator(self.app_name, self.parser, self.paths)
        api_client_generator.generate()

    def generate_api_client_setup_py(self):
        from django_swagger_utils.api_client.setup_py_generator import \
            SetupPyGenerator
        setup_py_generator = SetupPyGenerator(self.app_name, self.paths)
        setup_py_generator.setup_template()
        setup_py_generator.generate_init_file()

    def deploy_api_client(self):

        # dist command
        os.system("python setup.py sdist upload -r local")

        # deleting the generated files
        from shutil import rmtree
        try:
            os.rename(self.paths["client_manifest_path"] + ".old",
                      self.paths["client_manifest_path"])

            os.rename(self.paths["client_setup_py_path"] + ".old",
                      self.paths["client_setup_py_path"])
        except OSError:
            pass
        try:
            rmtree(self.paths['client_app_base_path'])
        except OSError:
            pass
        try:
            rmtree(self.paths['client_app_base_path_egg_info'])

        except OSError:
            pass
        # try:
        #     rmtree(self.paths['pypi_dist_path'])
        # except OSError:
        #     pass

    def generate_deploy_api_client(self):

        try:
            os.rename(self.paths["client_manifest_path"],
                      self.paths["client_manifest_path"] + ".old")
            os.rename(self.paths["client_setup_py_path"],
                      self.paths["client_setup_py_path"] + ".old")
        except OSError:
            pass

        self.generate_api_client_interface()
        self.generate_api_client()
        self.generate_api_client_constants()
        self.generate_api_client_setup_py()
        self.deploy_api_client()


class Command(BaseCommand):
    can_import_settings = True
    help = 'Generate views and docs from swagger spec files'

    def add_arguments(self, parser):
        parser.add_argument('-a', '--apis', action='store_true',
                            help='Build API Views')
        parser.add_argument('-t', '--thirdparty', action='store_true',
                            help='Build Third Party API Views')
        parser.add_argument('-l', '--lib', action='store_true',
                            help='Build Third Party API Views in lib directory for google ape')
        parser.add_argument('-co', '--cons', action='store_true',
                            help='Build Constants')
        parser.add_argument('--f', action='store_true', help='Build Constants')
        parser.add_argument('-d', '--docs', action='store_true',
                            help='Build Docs')
        parser.add_argument('-md', '--markdown', action='store_true',
                            help='Build Documentation')

        parser.add_argument('-j', '--jars', action='store_true',
                            help='Build Android Jars')
        parser.add_argument('-j2', '--jarsv2', action='store_true',
                            help='Build Android Jars V2')
        parser.add_argument('-m', '--mobx3', action='store_true',
                            help='To generate mobx classes from templates')
        parser.add_argument('-n', '--npm', action='store_true',
                            help='To upload generated mobx classes to npm library')
        parser.add_argument('-j1_gen', '--jars_v1_generation',
                            action='store_true',
                            help='Build Android Jars Genaration')
        parser.add_argument('-j1_deploy', '--jars_v1_deployment',
                            action='store_true',
                            help='Build Android Jars Deployment')
        parser.add_argument('-j2_gen', '--jars_v2_generation',
                            action='store_true',
                            help='Build Android Jars Genaration')
        parser.add_argument('-j2_deploy', '--jars_v2_deployment',
                            action='store_true',
                            help='Build Android Jars Deployment')
        parser.add_argument('-c', '--clean', action='store_true',
                            help='Clean Builds')
        parser.add_argument('-I', '--install', action='store_true',
                            help='install requirements for merge file splitting and merging')
        parser.add_argument('-M', '--merge', action='store_true',
                            help='Merge the spec file structure present in spec folder in api_spec folder')
        parser.add_argument('-S', '--split', action='store_true',
                            help='Split the present api_spec.json into further folders')
        parser.add_argument('app', nargs='*', type=str)
        parser.add_argument('-i', '--interfaces', action='store_true',
                            help='generate interfaces from spec files')
        parser.add_argument('-b', nargs=1, type=str)
        parser.add_argument('-sc', '--sync_spec', action='store_true',
                            help='If api spec needs to sync with dev')
        parser.add_argument('-sb', '--sgui_build', action='store_true',
                            help='generate api spec from swagger gui spec files')

        parser.add_argument('-api_client', '--api_client', action='store_true',
                            help='generate api client from spec files')

    @staticmethod
    def create_docs_index_html(apps):
        from django.conf import settings
        base_dir = settings.BASE_DIR
        docs_dir = os.path.join(base_dir, "docs")
        index_html = os.path.join(docs_dir, "index.html")
        list_items = ["<li><a href='./{app_name}/'>{app_name}</a></li>".format(app_name=app_name) for app_name in apps]
        index_html_contents = """<h1>List of Apps</h1>
<ul>{}</ul>""".format("".join(list_items))
        f = open(index_html, "w")
        f.write(index_html_contents)
        f.close()

    def handle(self, *args, **options):
        '''
        Handles the concerned activity
        :param args: aruguments user give in command line
        :param options: options to arguments given
        :return:
        '''

        from django.conf import settings
        import os
        base_dir = settings.BASE_DIR
        # obtain path of zappa_settings
        zappa_settings = os.path.join(base_dir, "zappa_settings.json")
        # set default domain as empty string
        domain = ''
        django_swagger_utils_settings = settings.SWAGGER_UTILS
        swagger_apps = list(django_swagger_utils_settings['APPS'].keys())

        third_party_swagger_apps = getattr(settings,
                                           'THIRD_PARTY_SWAGGER_APPS', [])
        # if domain specific url is required
        if options['b']:
            # check for existence of zappas_settings.json
            if os.path.exists(zappa_settings):
                with open(zappa_settings) as src_json:
                    zappa_settings_dict = json.load(src_json)
                    # checking if given branch exists
                    if options['b'][0] in zappa_settings_dict:
                        # replacing defaul domain with branch  domain
                        req_branch = options['b'][0]
                        domain = zappa_settings_dict[req_branch]['domain']
                    else:

                        # terminating
                        print("Given branch %s is not found" % options['b'][0])
                        exit(1)
            else:
                print("zappa_settings.json not found")
                exit(1)

        try:
            apps = options['app']
            if not apps:
                apps = swagger_apps

            for app in apps:
                if app in swagger_apps:
                    if options['sgui_build']:
                        # if option is to build the swagger spec from server
                        # validation not required because there might not be any spec file
                        build = Build(app, base_dir,
                                      django_swagger_utils_settings,
                                      is_validation_required=False)
                        build.generate_spec_from_sgui()
                    else:
                        build = Build(app, base_dir,
                                      django_swagger_utils_settings)

                    if options['apis']:
                        build.clean()
                    if options['docs']:
                        build.clean_docs()

            counter = 0
            build_docs_apps = []

            # calling the concerned build methods for each app
            for app in apps:
                if app in swagger_apps:
                    if options['sgui_build']:
                        # if option is to build the swagger spec from server
                        # validation not required because there might not be any spec file
                        build = Build(app, base_dir,
                                      django_swagger_utils_settings,
                                      is_validation_required=False)
                        build.generate_spec_from_sgui()
                    else:
                        build = Build(app, base_dir,
                                      django_swagger_utils_settings)

                    if options['sync_spec']:
                        build.sync_spec_from_sgui()

                    if options['apis']:
                        build.generate_specs_build()

                    if options['docs']:
                        build.generate_patch_build(domain)
                        build_docs_apps.append(app)

                    if options['markdown']:
                        build.create_documentation(app, counter)

                    if options['cons']:
                        override = False
                        if options['f']:
                            override = True

                        build.constant_gen(override)

                    if options['jars']:
                        Build(app, base_dir,
                              django_swagger_utils_settings).android_build()
                    if options['jarsv2']:
                        Build(app, base_dir,
                              django_swagger_utils_settings).android_build_v2()

                    if options['jars_v1_generation']:
                        vnum = build.get_version()
                        build.android_jar_genaration(vnum)
                    if options['jars_v1_deployment']:
                        vnum = build.get_version()
                        build.android_jar_deployment(vnum)
                    if options['jars_v2_generation']:
                        vnum = build.get_version()
                        build.android_jar_v2_genaration(vnum)
                    if options['jars_v2_deployment']:
                        vnum = build.get_version()
                        build.android_jar_v2_deployment(vnum)
                    if options['clean']:
                        build.clean()
                    if options['interfaces']:
                        override = False
                        if options['f']:
                            override = True
                        build.generate_interfaces(override)
                    if options['api_client']:
                        from colored import fg, attr
                        print("{}{}{}Generating API clients "
                              "for : {}".format(fg(2), attr(1), attr(4), app))
                        build.generate_deploy_api_client()
                    if options['mobx3']:
                        # to generate mobx classes in a folder mobx_classes in build folder
                        build.create_mobx_from_templates()
                    if options['npm']:
                        # to deploy the generated mobx classes under the name ib_appname_mobx
                        build.add_to_npm()

                    if options['install']:
                        # ->install necessary packages for merging and splitting the spec file
                        build.install_for_spec()
                    if options['merge']:
                        # ->merge the spec file which is present in parts in api_spec/specs folder
                        build.merge_spec()
                    if options['split']:
                        # ->split the spec file api_spec.json to specs/ folder
                        build.split_spec()

                else:
                    print(
                        "Ignoring %s app. Please add it in SWAGGER_UTILS['APPS'] first.")

            if options['docs']:
                self.create_docs_index_html(build_docs_apps)

            if options['thirdparty']:

                for third_party_app in third_party_swagger_apps:

                    third_party_base_dir = None
                    if options["lib"]:
                        third_party_base_dir = base_dir + "/lib"
                    else:
                        try:
                            third_party_base_dir = os.path.abspath(
                                os.path.join(__import__(third_party_app).
                                             __path__[0], os.pardir))
                        except ImportError:
                            raise

                    build = Build(app_name=third_party_app,
                                  base_dir=third_party_base_dir)
                    build.clean()
                    build.generate_specs_build()
        except Exception as err:
            print(err)
            raise


"""
Open API Specs (swagger.io) - DRF Server - IB Group

1. git clone https://bitbucket.org/rahulsccl/ib_service/
2. pip install -r requirements.txt
3. Open API Specs defined for app_b in app_b/api_specs/api_spec.json Ref
[Open API Specs](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md)
4. python common/swagger/utils/management/build_common.py [ this will generate spces base api server_gen ]
5. manage.py test <app_name>.build.tests
6. python manage.py runserver
7. look at 127.0.0.1:8000/api/app_b/user/1234/
"""
