import os

from django.core.management.base import BaseCommand

from .custom_app import CreateCustomApp


class CreateCleanApp(CreateCustomApp):
    def get_default_files_list(self):
        folders_list, files_list = super(CreateCleanApp,
                                         self).get_default_files_list()

        app_base_path = os.path.join(self.base_path, self.app_name)

        adapters_dir = os.path.join(app_base_path, "adapters")
        adapters_files = self._get_adapters_files(adapters_dir)
        constants_dir = os.path.join(app_base_path, "constants")
        constants_files = self._get_constants_files(constants_dir)
        exceptions_dir = os.path.join(app_base_path, "exceptions")
        app_interfaces_dir = os.path.join(app_base_path, "app_interfaces")
        interactors_dir = os.path.join(app_base_path, 'interactors')
        interactors_sub_folders, interactors_sub_files = \
            self._get_sub_folders_list_and_sub_files_list_for_interactors(
                interactors_dir)
        populate_dir = os.path.join(app_base_path, 'populate/')
        utils_dir = os.path.join(app_base_path, 'utils/')
        tests_dir = os.path.join(app_base_path, 'tests')
        test_sub_folders, test_sub_files = \
            self._get_sub_folders_list_and_sub_files_list_for_tests(tests_dir)

        extra_folders_list = {
            'entities_dir': os.path.join(app_base_path, 'entities/'),
            'storages_dir': os.path.join(app_base_path, 'storages/'),
            'presenters_dir': os.path.join(app_base_path, 'presenters/'),
            'exceptions_dir': exceptions_dir,
            'i_mixins': os.path.join(interactors_dir, 'mixins/'),
            'populate_dir': populate_dir,
            'utils_dir': utils_dir,
            # 'u_populate': os.path.join(utils_dir, 'populate/'),
        }
        extra_folders_list.update(interactors_sub_folders)
        extra_folders_list.update(test_sub_folders)

        extra_files_list = {
            'app_service_interface_file': (
                os.path.join(app_interfaces_dir, 'service_interface.py'), ""),
            'custom_exceptions_file': (
                os.path.join(exceptions_dir, 'custom_exceptions.py'), ""),
        }
        extra_files_list.update(adapters_files)
        extra_files_list.update(constants_files)
        extra_files_list.update(interactors_sub_files)
        extra_files_list.update(test_sub_files)

        folders_list.pop('validators_dir')
        folders_list.update(extra_folders_list)
        files_list.pop("fixture_file", "")
        files_list.update(extra_files_list)
        return folders_list, files_list

    @staticmethod
    def get_service_adapter_v3_content():
        from django_swagger_utils.utils.custom_app_templates.service_adapter_template_v3 import \
            service_adapter_template_v3
        from django.template.base import Template
        from django.template.context import Context
        service_adapter_init = Template(service_adapter_template_v3)
        service_adapter_content_v3 = service_adapter_init.render(Context())
        return service_adapter_content_v3

    @staticmethod
    def get_user_service_adapter_content():
        from django_swagger_utils.utils.custom_app_templates.user_service_adapter_template import \
            user_service_adapter_template
        from django.template.base import Template
        from django.template.context import Context
        service_adapter_init = Template(user_service_adapter_template)
        user_service_adapter_content = service_adapter_init.render(Context())
        return user_service_adapter_content

    @staticmethod
    def get_service_interface_content():
        from django_swagger_utils.utils.custom_app_templates.service_interface_template import \
            service_interface_template
        from django.template.base import Template
        from django.template.context import Context
        service_adapter_init = Template(service_interface_template)
        user_service_adapter_content = service_adapter_init.render(Context())
        return user_service_adapter_content

    @staticmethod
    def _get_sub_folders_list_and_sub_files_list_for_interactors(
        interactors_dir) -> tuple:
        i_presenter_interfaces_dir = os.path.join(
            interactors_dir, 'presenter_interfaces')
        i_storage_interfaces_dir = os.path.join(
            interactors_dir, 'storage_interfaces')
        i_mixins_dir = os.path.join(interactors_dir, 'mixins/')
        interactors_sub_folders_list = {
            'i_presenter_interfaces_dir': i_presenter_interfaces_dir,
            'i_storage_interfaces_dir': i_storage_interfaces_dir,
            'i_mixins_dir': i_mixins_dir
        }
        interactors_sub_files_list = {
            'i_presenter_interface_file': (
                os.path.join(i_presenter_interfaces_dir,
                             'presenter_interface.py'), ""),
            'i_presenter_interface_dtos_file': (
                os.path.join(i_presenter_interfaces_dir,
                             'dtos.py'), ""),
            'i_storage_interface_file': (
                os.path.join(i_storage_interfaces_dir,
                             'storage_interface.py'), ""),
            'i_storage_interface_dtos_file': (
                os.path.join(i_storage_interfaces_dir,
                             'dtos.py'), ""),
        }
        return interactors_sub_folders_list, interactors_sub_files_list

    def _get_adapters_files(self, adapters_dir) -> dict:
        return {
            'a_dtos': (os.path.join(adapters_dir, 'dtos.py'), ""),
            'a_service_adapter_file': (
                os.path.join(adapters_dir, 'service_adapter.py'),
                self.get_service_adapter_v3_content()),
            # 'a_user_service_adapter_file': (
            #     os.path.join(adapters_dir, 'user_service_adapter.py'),
            #     self.get_user_service_adapter_content()),
        }

    @staticmethod
    def _get_sub_folders_list_and_sub_files_list_for_tests(
        tests_dir) -> tuple:
        t_common_fixture_dir = os.path.join(tests_dir, 'common_fixtures')
        t_factories_dir = os.path.join(tests_dir, 'factories')
        test_sub_folders_list = {
            't_entities': os.path.join(tests_dir, 'entities/'),
            't_interactors': os.path.join(tests_dir, 'interactors/'),
            't_presenters': os.path.join(tests_dir, 'presenters/'),
            't_storages': os.path.join(tests_dir, 'storages/'),
            't_views': os.path.join(tests_dir, 'views/'),
            't_common_fixtures': t_common_fixture_dir,
            't_factories': t_factories_dir,
            't_interface': os.path.join(tests_dir, 'interfaces/'),
            't_populate': os.path.join(tests_dir, 'populate/'),
        }
        test_sub_files_list = {
            't_common_fixtures_adapters_file': (
                os.path.join(t_common_fixture_dir, 'adapters.py'), ""),
            't_common_fixtures_storages_file': (
                os.path.join(t_common_fixture_dir, 'storages.py'), ""),
            't_factories_adapter_dtos': (
                os.path.join(t_factories_dir, 'adapter_dtos.py'), ""),
            't_factories_models': (
                os.path.join(t_factories_dir, 'models.py'), ""),
            't_factories_presenter_dtos': (
                os.path.join(t_factories_dir, 'presenter_dtos.py'), ""),
            't_factories_storage_dtos': (
                os.path.join(t_factories_dir, 'storage_dtos.py'), ""),
        }
        return test_sub_folders_list, test_sub_files_list

    @staticmethod
    def _get_constants_files(constants_dir) -> dict:
        return {
            'config_constant_file': (
                os.path.join(constants_dir, 'config.py'), ""),
            'enum_constant_file': (
                os.path.join(constants_dir, 'enum.py'), ""),
            'exception_messages_constant_file': (
                os.path.join(constants_dir, 'exception_messages.py'), ""),
        }


class Command(BaseCommand):
    can_import_settings = True
    help = 'Generate a clean architecture based template app'

    def add_arguments(self, parser):
        parser.add_argument('apps', nargs='*', type=str,
                            help="List of apps to create")
        parser.add_argument('-p', '--project', type=str,
                            help="Name of the django project",
                            required=True)

    def handle(self, *args, **options):
        from django.conf import settings
        base_dir = settings.BASE_DIR
        try:
            apps = options['apps']
            project = options['project']
            if project not in base_dir:
                self.stderr.write(self.style.ERROR(
                    '**** ERROR: Project name is not right ****'))
                exit(1)
            if not apps:
                self.stderr.write(
                    "usage: python manage.py create_cleanapp <app_names> ")
                exit(1)
            for app_name in apps:
                create_clean_app = CreateCleanApp(app_name, base_dir,
                                                  project)
                create_clean_app.create_app()
        except Exception as err:
            self.stderr.write(err)
            exit(1)
