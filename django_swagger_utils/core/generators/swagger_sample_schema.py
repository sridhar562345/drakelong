# coding=utf-8

import json

from django_swagger_utils.drf_server.utils.server_gen.string_gen import Xeger


class SwaggerSampleSchema(object):
    def __init__(self, definitions, json_schema, definition_name=None):
        self.definitions = definitions
        self.json_schema = json_schema
        self.definition_name = definition_name

    def get_definition_json(self, definition_name):
        """
        returns def dict
        :param definition_name:
        :return:
        """
        if definition_name == self.definition_name:
            return {}
        definition = self.definitions[definition_name]
        swagger_sample_json = SwaggerSampleSchema(self.definitions, definition,
                                                  definition_name)
        return swagger_sample_json.get_data_dict()

    @staticmethod
    def merge_dicts(dict1, dict2):
        """

        :param x:
        :param y:
        :return:
        """
        try:
            res_dict = dict1.copy()
            res_dict.update(dict2)
        except ValueError:
            if list == type(dict1) or type(dict2) == list:
                print("both all of definations should be of type object not a array")
                print("definition 1: ", dict1)
                print("-----------------------------------------------------------------------")
                print("definition 2:", dict2)
                print("------------------------------------------------------------------------")
                print("BUILD FAILURE")
                exit(1)
        return res_dict

    def get_data_dict(self, schema=None):
        if not schema:
            schema = self.json_schema
        if schema is None:
            return None

        schema_type = schema.get("type", None)
        format = schema.get("format", None)
        enum = schema.get("enum", None)
        schema_ref = schema.get("$ref", None)
        schema_all_of = schema.get("allOf", None)
        if schema_type == "string" and schema.get("pattern", None):
            x = Xeger()
            regex = "r'%s'" % (schema.get("pattern", None))

            data = str(x.xeger(regex))
            return data[2:len(data) - 1]
        if schema_type in ["integer", "string", "boolean", "number"]:
            data = self.get_primitive_data_type(schema_type, format=format,
                                                enum=enum)
        elif schema_type in ["array", "object_array"]:
            array_schema = schema.get("items")
            data_item = self.get_data_dict(array_schema)
            data = [data_item]
        elif schema_ref:
            schema_split = schema_ref.split("#/definitions/")
            definition_name = schema_split[1]
            data = self.get_definition_json(definition_name)
        elif schema_all_of:
            data = self.get_all_of_dict(schema_all_of)
        else:
            data = self.object_data_dict(schema)
        return data

    def get_all_of_dict(self, all_of_props):
        data = {}
        for each_schema in all_of_props:
            swagger_sample_json = SwaggerSampleSchema(self.definitions,
                                                      each_schema,
                                                      self.definition_name)
            data = self.merge_dicts(data, swagger_sample_json.get_data_dict())
        return data

    def object_data_dict(self, schema):
        """
        returns object dict from the properties in spec
        :param schema: swagger spec
        :return: object data dictionary
        """
        properties = schema.get("properties", None)
        if not properties:
            raise KeyError("'properties' key is missing")

        schema_type = schema.get("type", None)
        if schema_type != "object":
            raise Exception("invalid type value - expected 'object'")

        data = {}
        for property_name, each_property in list(properties.items()):
            swagger_sample_json = SwaggerSampleSchema(self.definitions,
                                                      each_property,
                                                      self.definition_name)
            data[property_name] = swagger_sample_json.get_data_dict()
        return data

    def to_json(self, indent=4):
        """
        returns json or string of dict
        :param indent: fixed to 4 for clear presentation
        :return:
        """
        data = self.get_data_dict()
        if isinstance(data, dict) or (
            isinstance(data, list) and not isinstance(data[0], list)):
            if indent:
                return json.dumps(data, indent=indent)
            else:
                return json.dumps(data)
        else:
            return str(data)

    def get_json(self):
        """
        loads str into json
        :return:
        """

        json_str = self.to_json()
        import json
        try:
            return json.loads(json_str)
        except Exception as e:
            print("Error [swagger_sample_schema.py: 133]: ", e)
            return {}

    @staticmethod
    def get_primitive_data_type(data_type, **kwargs):
        """
        return a mock response for each datatype
        :param data_type:
        :param kwargs:
        :return:
        """
        if data_type == "integer":
            return 1
        elif data_type == "number":
            return 1.1
        elif data_type == "string":
            enum = kwargs.pop('enum', [])
            if kwargs.get('format', None) == "email":
                return "string@string.com"
            elif kwargs.get('format', None) == "date":
                return "2099-12-31"
            elif kwargs.get('format', None) == "date-time":
                return "2099-12-31 00:00:00"
            elif kwargs.get('format', None) == "time":
                return "00:00:00"
            elif kwargs.get('format', None) == "uuid":
                return "89d96f4b-c19d-4e69-8eae-e818f3123b09"
            elif enum:
                return enum[0]
            return "string"
        elif data_type == "boolean":
            return True
        else:
            raise Exception("Invalid primitive data type: %s" % data_type)
