from django_swagger_utils.drf_server.fields.boolean_field import boolean_field
from django_swagger_utils.drf_server.fields.integer_field import integer_field
from django_swagger_utils.drf_server.fields.number_field import number_field
from django_swagger_utils.drf_server.fields.string_field import string_field


def path_param_field(param, parameter_key_name=None, param_name=None):
    if not param_name:
        param_name = param["name"]

    if not parameter_key_name:
        # in case of available parameters, we use the value of parameter name #/parameters/<name>, in other places
        # we are keeping the parameter.name as parameter_key_name
        parameter_key_name = param_name

    from django_swagger_utils.core.utils.case_convertion import to_camel_case
    context_properties = {
        "param_name_camel_case": to_camel_case(param_name),
        "param_name": parameter_key_name,
        "param_field_name": param_name,
        "param_serializer": "",
        "param_serializer_import_str": "",
        "param_serializer_field": "",
        "param_url_regex": "",
        "url_regex": "",
        "example_url_regex": "",
        "param_example": ""
    }
    param_type = param.get("type", None)
    param_format = param.get("format", None)
    param_required = param.get("required", False)
    if not param_type:
        raise Exception(
            "property 'type' not defined for form param : %s : %s" % (
                param_name, parameter_key_name))
    if param_type == "integer":
        url_regex = "\d+"
        example_url_regex = "1234"
        context_properties["param_serializer_field"], context_properties[
            "param_example"] = \
            integer_field(param, param_required, return_example=True)
    elif param_type == "number":
        url_regex = "\d+(?:\.\d+)?"
        example_url_regex = "12.12"
        context_properties["param_serializer_field"], context_properties[
            "param_example"] = \
            number_field(param, param_required, return_example=True)
    elif param_type == "string" and param_format == "uuid":
        url_regex = "[0-9a-f-]+"
        example_url_regex = "413642ff-1272-4990-b878-6607a5e02bc1"
        context_properties["param_serializer_field"], context_properties[
            "param_example"] = \
            string_field(param, param_required, return_example=True)
    elif param_type == "string":
        # single word, no spaces allowed in param name
        url_regex = "[-\w]+"
        example_url_regex = "ibgroup"
        context_properties["param_serializer_field"], context_properties[
            "param_example"] = \
            string_field(param, param_required, return_example=True)
    elif param_type == "boolean":
        url_regex = "true|false"
        example_url_regex = "true"
        context_properties["param_serializer_field"], context_properties[
            "param_example"] = \
            boolean_field(param, param_required, return_example=True)
    elif param_type == "array":
        collection_format = param.get("collectionFormat", "csv")

        from django_swagger_utils.drf_server.utils.server_gen.collection_fromat_to_separator import \
            collection_format_to_separator_regex
        separator = collection_format_to_separator_regex(collection_format)
        inner_array_param = param.get("items")
        inner_array_context_properties = path_param_field(inner_array_param,
                                                          param_name=param_name,
                                                          parameter_key_name=parameter_key_name)
        array_param_regex = inner_array_context_properties["url_regex"]
        array_param_example_regex = inner_array_context_properties[
            "example_url_regex"]
        url_regex = "%s(%s%s)*" % (
            array_param_regex, separator, array_param_regex)
        example_url_regex = "%s%s%s" % (
            array_param_example_regex, separator, array_param_example_regex)
        from django_swagger_utils.drf_server.fields.collection_array_field import \
            get_array_field
        context_properties["param_serializer_field"], context_properties[
            "param_example"] = \
            get_array_field(param.get("items"), param_name, collection_format,
                            return_example=True)
    else:
        raise Exception("Invalid value for type of form param")
    context_properties["param_url_regex"] = r"(?P<%s>%s)" % (
        param_name, url_regex)
    context_properties["url_regex"] = url_regex
    context_properties["example_url_regex"] = example_url_regex
    return context_properties
