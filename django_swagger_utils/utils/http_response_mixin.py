class HTTPResponseMixin:

    @staticmethod
    def prepare_http_response_object(response_dict, status):
        from django.http import HttpResponse
        import json
        return HttpResponse(content=json.dumps(response_dict), status=status)

    def prepare_200_success_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=200)

    def prepare_201_created_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=201)

    def prepare_400_bad_request_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=400)

    def prepare_401_unauthorized_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=401)

    def prepare_403_forbidden_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=403)

    def prepare_404_not_found_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=404)

    def prepare_405_method_not_allowed_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=405)

    def prepare_417_expectation_mismatch_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=417)

    def prepare_500_internal_server_error_response(self, response_dict):
        return self.prepare_http_response_object(response_dict=response_dict, status=500)
