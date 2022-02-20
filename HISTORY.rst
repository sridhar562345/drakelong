.. :changelog:

History
-------

2.2.7 (2021-02-04)
+++++++++++++++++++

- Added support for `DSU_HEADER_META_KEYS_TO_LOG` and `DSU_KEYS_TO_MASK`
- Removed `HTTP_AUTHORIZATION` from default headers logging

2.2.6 (2021-01-21)
+++++++++++++++++++

Updated res status enum and http status code for below common errors

```
"OperationalError": {
    "http_status_code": 503,
    "res_status": "DB_MAINTENANCE_ERROR"
},
"InternalError": {
    "http_status_code": 503,
    "res_status": "DB_MAINTENANCE_ERROR"
},
```

2.2.5 (2020-11-03)
+++++++++++++++++++
Added support for - in url path param fields


2.2.4 (2020-10-03)
+++++++++++++++++++
Added database exceptions handling for 500 status codes in handle_custom_exceptions

```
"OperationalError": {
    "http_status_code": 500,
    "res_status": "DB_ERROR"
},
"InternalError": {
    "http_status_code": 500,
    "res_status": "DB_ERROR"
},
"DatabaseError": {
    "http_status_code": 500,
    "res_status": "DB_ERROR"
},
"IntegrityError": {
    "http_status_code": 500,
    "res_status": "DB_ERROR"
},
"NotSupportedError": {
    "http_status_code": 500,
    "res_status": "DB_ERROR"
}
```

2.2.3 (2020-09-03)
+++++++++++++++++++
bug fix about generating snapshots in apis without security in dsu version 1

2.2.2 (2020-0-24)
+++++++++++++++++++
Fixed constant value for the uuid in swagger_sample_schema.py [backward compatible]
So while build the app then request_and_response_mock file uuid field value get the same constant value.
That is "89d96f4b-c19d-4e69-8eae-e818f3123b09"


2.2.1 (2020-08-04)
+++++++++++++++++++
1. Bugfix in request_response_wrapper (Change default value to {} from None)


2.2.0 (2020-07-11)
+++++++++++++++++++
1. Renamed `test_v1.py` to `test_utils.py`
2. Renamed `default_test_case` method in `django_swagger_utils.utils.test_utils.TestUtils` to `make_api_call` [reason readability]
3. Added `yapf` to generate formatted test case template
4. Removed `__all__` generation for snapshot tests files for latest file `dsu_version` >= 1.0


2.1.0 (2020-07-11)
+++++++++++++++++++
Updated & Added below features -> [ backward compatible ]
1. Added Validation for the HttpResponse content. It means Serialize the HttpResponse content
2. Added path_params, query_params key attributes in kwargs. Both path_params and query params contain the python dictionary.
     Let's see the below example code for more understanding
     ```python
        path_pramas = kwargs["path_params"]
        post_id = path_params["post_id"]

        query_params = kwargs["query_params"]
        off_set = query_params["off_set"]
     ```
3. Added the respected python datatype for path_params values.
    Let's see the below post example code where post_id is int type
    ```python
        path_pramas = kwargs["path_params"]
        post_id = path_params["post_id"]
        assert isinstance(post_id, int)
    ```
4. Moved the tests from the views folder to the test's views folder. So In view folder only contains the controller logic.
5. Updated the version of TestUtils class(snapshot test_case_01.py) is added to DSU for supporting the following features
      1. To Support pytest style fixtures
      2. pytest --snapshot-update
      3. Support multiple(related) tests in the same test class
      4. Support the backward compatible using version control
     Note:- Boolean data type path params must be string in test cases because not handle in new TestUtils file for snapshot testing
6. Added the version control for supporting new dsu to the previous projects.
   By default, dsu_version is "0.0" and If not mention any "dsu_version" key it takes as the default version.
        Example for existing previous project, Added version control in the base_swagger_utils.py
        ```python
            SWAGGER_UTILS = {
                 "APPS": {
                     "nkb_resources": { "dsu_version": "1.0" },
                     "nkb_discussions": {}, # default dsu_vesion("0.0")
                }
        ```

7. Added "DSU_RAISE_EXCEPTION_FOR_API_RESPONSE_STATUS_CODE" constant in the base_swagger_utils.py file. By default, its value is "false".
   If you change the value to true then you need to mention all HttpResponse (like 200, 404, 403, etc) in the spec.
        For example, I do not mention a 404 response in API spec
        but I set DSU_RAISE_EXCEPTION_FOR_API_RESPONSE_STATUS_CODE to "True" then dsu raise below exception
        ```python
            ResponseNotDefined('Response for Status Code 404 Not Defined')
        ```
8. Grouping the similar (related) views using the "x-group" keyword in API spec.
9. Added Common HttpResponse Decorators for the presenter in "/django_swagger_utils/utils/http_response_mixin.py"
    Example presenter implementation
    ```python
        class JsonPresenter(Presenter, HTTPResponseMixin):
            def get_response_create_post(self, post_id: int):
                response = {
                    "post_id": post_id
                }
                return self.prepare_201_created_response(response_dict=response)
    ```
10. we have deprecated the check_use_case functionality in the des_version "1.0".
    In the default dsu version("0.0") the "check_use_case" functionality working fine

2.0.23 (2020-07-07)
+++++++++++++++++++
Updated the below folder structure for create_cleanapp
1. Remove the user_service_adapter.py file from adapter folder [ backward compatible ]
2. Remove the fixture.py file from utils folder [ backward compatible ]
3. Added config.py file in Constants folder
4. Rename the exception_classes.py to custom_exception.py in exceptions folder
5. presenter folder Rename to presenter_interfaces in Interactor folder
6. storages folder Rename to storage_interfaces in Interactor folder
7. Added dtos.py file in the presenter_interfaces and storage_interface folder
8. Added the populate folder
9. Added the common_fixture, factories, interfaces and populate folders in tests folder




2.0.22 (2020-07-02)
+++++++++++++++++++

Added index.html with list of apps for build -d command in docs folder. [ backward compatible ]

Note: If you have any existing docs pointing <project_name>/<branch> please update them, as the previous files in
s3 will get replaced.

2.0.21 (2020-07-02)
+++++++++++++++++++

- Included aws s3 sync for s3push command  [ backward compatible ] [but need aws cli setup from now on]

pip install awscli

Once after build -d command do `pip uninstall awscli` to optimize the codeship build size.

2.0.20 (2020-07-01)
+++++++++++++++++++

- Bug fix about build -d clean's apis also, added clean_docs method  [ backward compatible ]

2.0.19 (2020-06-30)
+++++++++++++++++++

- Added new folder structure in create_cleanapp command [ backward compatible ]

2.0.18 (2020-01-31)
+++++++++++++++++++

- Added support for append_slash false [ backward compatible ]

2.0.17 (2019-09-26)
+++++++++++++++++++

- Added support for uuid in path parameters, with type "string" and format "uuid"

2.0.16 (2019-09-17)
+++++++++++++++++++

- Added support for x-issue-links and docs generation

2.0.15 (2019-08-01) - backward compatible

++++++++++++++++++

Using singleton for local.thread()

2.0.14 (2019-08-01) - backward compatible

++++++++++++++++++

bug fix related operation_id not coming in loggers

2.0.13 (2019-07-13) - backward compatible

++++++++++++++++++

bug fix drf custom exception handler


2.0.12 (2019-06-17) - backward compatible

++++++++++++++++++

bug fix in swagger-ui rendering

2.0.11 (2019-06-16) - backward incompatible

++++++++++++++++++

removed allow from test header parameters

2.0.10 (2019-06-15) - backward compatible

++++++++++++++++++

bug fix in user dto


2.0.9 (2019-06-15) - backward compatible

++++++++++++++++++

bug fix in user dto

2.0.8 (2019-06-15) - backward compatible

++++++++++++++++++

bug fix in validate opertion id and group name function

2.0.7 (2019-06-12) - backward compatible

++++++++++++++++++

added support to group apis


2.0.6 (2019-06-12) - backward compatible

++++++++++++++++++

added support to access user_dto in api_wrapper, validator class


2.0.5 (2019-06-12) - backward compatible

++++++++++++++++++

added support to access user_dto in api_wrapper


2.0.4 (2019-06-12) - backward compatible

++++++++++++++++++

ordered snapshot test case header parameters


2.0.3 (2019-06-12) - backward compatible

++++++++++++++++++

ordered snapshot test case header parameters


2.0.2 (2019-06-12) - backward compatible

++++++++++++++++++

bug fix in accessing user object pk


2.0.1 (2019-06-11) - backward compatible

++++++++++++++++++

bug fix in accessing exception content


2.0.0 (2019-05-23) - backward incompatible

++++++++++++++++++

added python3(3.7) support
removed python2 support


1.3.32 (2019-05-16) - backward compatible

++++++++++++++++++

bug fix in request data log


1.3.31 (2019-05-16) - backward compatible

++++++++++++++++++

Handling 8kb limit in logs

1.3.30 (2019-05-16) - backward compatible

++++++++++++++++++

Added dsu reset data middleware

1.3.29 (2019-05-16) - backward compatible

++++++++++++++++++

removed user info from new request log


1.3.28 (2019-05-10) - backward compatible

++++++++++++++++++

bug fix related to optional object none case in all off

1.3.27 (2019-05-09) - backward compatible

++++++++++++++++++

bug fix related to optional object none case in response


1.3.26 (2019-04-28) - backward compatible

++++++++++++++++++

added support for two mandatory logs and log filters related api request and response

to disable existing dsu response time log and api name logs use

`LOG_DSU_OLD_VERSION_LOGS = False` in your settings


1.3.25 (2019-04-22)

++++++++++++++++++

* added support for `DJANGO_SWAGGER_UTILS_SKIP_URL_TAGS` to skip them in url.py

by default all urls will be generated, if you specify a tag in `DJANGO_SWAGGER_UTILS_SKIP_URL_TAGS` these will not be generated in `urls.py`

Note: This a entire project specific settings, not at individual app

Usage:

environment specific settings local.py / alpha.py / appropriate env .py


DJANGO_SWAGGER_UTILS_SKIP_URL_TAGS = [
    'internal-testing'
]


add this tag in each operationId respective tag


{
    ...
    "operationId": "delete_user",
    "tags": [
        ...
        "internal-testing"
        ...
    ]
}


1.3.24 (2019-02-28)

++++++++++++++++++

* updated `jsonschema` requirement version

1.3.23 (2018-12-22)

++++++++++++++++++

* added additional error codes for in mock response and

1.3.22 (2018-12-16)

++++++++++++++++++

* reverted support for default mocking of request id


1.3.21 (2018-12-15)

++++++++++++++++++

* added support for default mocking of request id

1.3.20 (2018-12-13)

++++++++++++++++++

* swagger ui deep linking enabled and updated with latest swagger ui @3.20.2

1.3.19 (2018-12-13)

++++++++++++++++++

* method not allowed http status code changed to 405 instead of 500

1.3.18 (2018-12-13)

++++++++++++++++++

* signal template updated in custom_app command


1.3.17 (2018-12-05)

++++++++++++++++++

* bug fix related build -d

specify list of dirs to exclude in api doc building using

Ex:

settings.API_DOC_EXCLUDE_DIRS = [
    "node_modules",
    ".venv"
]

1.3.16 (2018-11-27)

++++++++++++++++++

* bug fix related to 201 response status code

1.3.15 (2018-11-27)

++++++++++++++++++

* bug fix related to 201 response status code

1.3.14 (2018-10-19)

++++++++++++++++++

* Added support for custom exception for http status code 500

1.3.13 (2018-10-04)

++++++++++++++++++

* Added support for custom scopes


1.3.12 (2018-10-03)

++++++++++++++++++

* Interface template bug fix

1.3.11 (2018-08-09)

++++++++++++++++++

* Fixes: Default initialization of foo_user

1.3.10 (2018-08-09)

++++++++++++++++++

* updated traceback related changes

1.3.9 (2018-08-08)

++++++++++++++++++

* updated build -d command and skipping updating apidoc command


1.3.8 (2018-08-02)

++++++++++++++++++

* added changes related to test cases foo user
-------
1.3.7 (2018-07-26)

++++++++++++++++++

* added username, password in old style of test case header type of auth

1.3.6 (2018-07-03)

++++++++++++++++++

* added mock ib request id in snapshot test case and removed print statements

1.3.5 (2018-06-19)

++++++++++++++++++

* templates lint issues corrected

1.3.4 (2018-06-16)

++++++++++++++++++

* bug fix in api client


1.3.3 (2018-06-16)

++++++++++++++++++

* ignored snapshot and request response mock files in lint


1.3.2 (2018-05-14)

++++++++++++++++++

* Minor bug fix

1.3.1 (2018-05-14)

++++++++++++++++++

* Application create changed to get_or_create in CustomTestUtils

1.3.0 (2018-05-09)
+++++++++++++++++++

* request data related changes integrated, date time fields are backward incompatible

1.2.18 (2018-05-07)
+++++++++++++++++++

* grouped multiple loggers into single logger

1.2.17 (2018-05-05)
+++++++++++++++++++

* added unicode to response content in exception messages

1.2.16 (2018-04-23)
+++++++++++++++++++

* removed value error from default list

1.2.15 (2018-04-13)
+++++++++++++++++++

* swagger ui bug fix

1.2.14 (2018-04-13)
+++++++++++++++++++

* swagger ui dist generator added

1.2.13 (2018-04-12)
+++++++++++++++++++
* error response logs updated

1.2.12 (2018-04-11)
+++++++++++++++++++
* snapshot test cases assert snapshots updated

1.2.11 (2018-04-06)
+++++++++++++++++++
* changes in lint management command

1.2.10 (2018-04-06)
+++++++++++++++++++
* changes in lint management command
* 'continue' instead of 'raise' incase of no pyfiles in app
* 'raise Exception' instead of 'raise' while catching SystemExit exception during 'Run(args)'

1.2.9 (2018-04-06)
++++++++++++++++++
added -E option to lint management command

1.2.8 (2018-03-30)
++++++++++++++++++

* bug fix in all of serializer

1.2.7 (2018-03-29)
++++++++++++++++++

* Now an extra module `url_groups` will be generated in `build/` folder which
will contain `url_patterns` grouped by tags defined in the API Specification
file. This will enable developer to import only subset of urls defined by an
app in root `urls.py` if he requires. As of now the tags will be applied on
the endpoint level (Which means if there are multiple methods accepted on an
endpoint with different tags, the endpoint will be tagged with all the tags.)


1.2.6 (2018-03-29)
++++++++++++++++++

* added a field in 'Latency' model - total_duplicate_queries

1.2.5 (2018-03-26)
++++++++++++++++++

* bug fix in mobx jinja2 templates

1.2.4 (2018-03-26)
++++++++++++++++++

* bug fix in auth class


1.2.3 (2018-03-26)
++++++++++++++++++

* merged mobx generator


1.2.2 (2018-03-26)
++++++++++++++++++

* bug fix in swagger ui view


1.2.1 (2018-03-23)
++++++++++++++++++

* bug fix in request_response

1.2.0 (2018-03-23)
++++++++++++++++++

* Switched to Jinja2 Templating from Django Templating for better readability and features
* Switched to Snapshot Testcases and made them the default option.
* Added Management Command create_snapshottest with args similar to create_testcase

### Advantages of using the new Snapshot Tests

* With snapshot tests you need not update the testcases manually everytime. You can use `--snapshot-update` option to automatically update all the responses automatically to match the latest results.
* You can directly use `python manage.py test` to run all the testcases. (Ensure that you do not have __init__.py in your project root directory.) Also do not forget to add the `TEST_RUNNER = 'snapshottest.django.TestRunner'`
* Better visible Comparision when there are differences b/w outputs
* You can go through https://github.com/syrusakbary/snapshottest for further details

1.1.90 (2018-03-19)
+++++++++++++++++++

* added a field in 'Latency' table - total_duplicate_queries

1.1.90 (2018-03-19)
+++++++++++++++++++

* minor change in mocktests management command for concurrency option

1.1.89 (2018-03-17)
+++++++++++++++++++

* updated timezone.now issue in custom test case

1.1.88 (2018-02-27)
+++++++++++++++++++

* added support for API_KEY_AUTHENTICATION_CLASS

1.1.87 (2018-02-25)
+++++++++++++++++++

* added support for STORE_LATENCY_OBJECT setting to insert latency object

1.1.86 (2018-02-08)
+++++++++++++++++++

* modified print statements in custom test case

1.1.85 (2018-02-08)
+++++++++++++++++++

* removed print statements in custom test case

1.1.84 (2018-02-08)
+++++++++++++++++++

* reverted --settings changes in mocktests

1.1.83 (2018-02-08)
+++++++++++++++++++

* added --settings support for mocktests

1.1.82 (2018-02-02)
+++++++++++++++++++

* Markdown bug fixed - removed operation_id in the api path

1.1.81 (2018-01-31)
+++++++++++++++++++

* Markdown bug fixed

1.1.80 (2018-01-06)
+++++++++++++++++++

* updated django version

1.1.79 (2018-01-06)
+++++++++++++++++++

* py2-3 compatibility


1.1.78 (2017-12-25)
+++++++++++++++++++

* updated the custom app content

1.1.77 (2017-12-01)
+++++++++++++++++++

* added missing commas in exceptions __init__

1.1.76 (2017-11-30)
+++++++++++++++++++

* bug fixes in number field

1.1.75 (2017-11-29)
+++++++++++++++++++

* api client conn bug fix

1.1.74 (2017-11-29)
+++++++++++++++++++

* $ref bug fix in constants generation

1.1.73 (2017-11-29)
+++++++++++++++++++

* changes the logger name in response_time

1.1.72 (2017-11-28)
+++++++++++++++++++

* enabled multi processing capability for linter to use the maximum no of cores


1.1.71 (2017-11-26)
+++++++++++++++++++

* changes in logger for printing api response, operation id and latency info


1.1.70 (2017-11-25)
+++++++++++++++++++

* bug fix in mobx generator
* changed the print statements in request response logging to logger.debug

1.1.69 (2017-11-22)
+++++++++++++++++++

* bug fix in body parameter overriding

1.1.68 (2017-11-22)
+++++++++++++++++++

* constants enum will be available in api_client

1.1.67 (2017-11-22)
+++++++++++++++++++

* added support for arrays as definition
* added support for allOf as item in array
* added support for direct ref to another definition in definitions
* updated custom_app cmd to new folder structure
* updated build -c clean command to clear all compiled python files
* added support for build -api_client cmd -> this will generate a api_client,
  constants and interface files as separate package `<app_name>_client`
* added support for missing use cases in constants generation
* updated indent=4 for api_spec patch files
* bug fixes in enum generation in type array, string

0.1.0 (2016-06-09)
++++++++++++++++++

* First release on PyPI.
