import json

from django.http import HttpResponse


def unwrap_response_dict(response):
    if not response or type(response) != dict:
        return response

    http_status_code = response.get('http_status_code', None)
    response_value = response.get("response", "")
    res_status = response.get("res_status", "")

    if http_status_code is None:
        return response

    from django_swagger_utils.drf_server.exceptions import Forbidden, NotFound, \
        ExpectationFailed, Unauthorized, BadRequest, CustomException, \
        FourXXException, FiveXXException

    if http_status_code == 400:
        raise BadRequest(response_value, res_status=res_status)
    elif http_status_code == 401:
        raise Unauthorized(response_value, res_status=res_status)
    elif http_status_code == 403:
        raise Forbidden(response_value, res_status=res_status)
    elif http_status_code == 404:
        raise NotFound(response_value, res_status=res_status)
    elif http_status_code == 417:
        raise ExpectationFailed(response_value, res_status=res_status)
    elif http_status_code == 500:
        raise CustomException(response_value, res_status=res_status)
    elif http_status_code in range(400, 500):
        raise FourXXException(response_value, res_status=res_status)
    elif http_status_code in range(500, 600):
        raise FiveXXException(response_value, res_status=res_status)
    return response


def mock_response(app_name, operation_name, test_case, kwargs,
                  default_response_body=None, group_name='', status_code=200):
    from django_swagger_utils.drf_server.utils.server_gen.check_use_case \
        import check_use_case
    default_response = {
        'status': 200,
        'body': {},
        'header_params': None
    }
    if default_response_body is not None:
        default_response['body'] = default_response_body
        default_response['status'] = status_code
    test_case = check_use_case(
        test_case, kwargs, app_name, operation_name, group_name)

    response_data = test_case.get("response", default_response)
    content = response_data["body"]
    status = response_data["status"]
    try:
        if isinstance(content, dict) or isinstance(content, list):
            content = json.dumps(content, indent=4)
        response = json.loads(content)
    except Exception as err:
        response = HttpResponse(content=content, status=status)

    response = unwrap_response_dict(response)
    from django_swagger_utils.drf_server.utils.server_gen.endpoint_response import \
        endpoint_response
    response = endpoint_response(response, response_data["status"],
                             response_data["header_params"])
    return response
