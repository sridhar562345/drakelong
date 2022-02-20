def string_field(properties, required=True, return_example=False):
    options_list = []
    field = "CharField"

    if not required:
        options_list.append("required=False")
        options_list.append("allow_blank=True")
        options_list.append("allow_null=True")

    description = properties.get("description", None)
    if description:
        options_list.append("help_text=\"%s\"" % description)

    default = properties.get("default", None)
    if default:
        options_list.append("default=\"%s\"" % default)

    max_length = properties.get("maxLength", None)
    if max_length:
        options_list.append("max_length=%d" % max_length)

    min_length = properties.get("minLength", None)
    if min_length:
        options_list.append("min_length=%d" % min_length)

    # byte - base64encoded string, binary, password # not supported by us
    format = properties.get("format", None)

    # re.compile(r'^[0-9]')
    # pattern can be ^[0-9]
    pattern = properties.get("pattern", None)

    # enum list of strings
    enum = properties.get("enum", None)

    example_string = "string"
    # time field not supported in swagger specs follow this issue
    # https://github.com/OAI/OpenAPI-Specification/issues/607
    if format == "date":
        field = "DateField"
        example_string = "2099-12-31"
        if not required:
            options_list.remove("allow_blank=True")
    elif format == "date-time":
        field = "DateTimeField"
        example_string = "2099-12-31 00:00:00"
        options_list.append("format='%Y-%m-%d %H:%M:%S'")
        if not required:
            options_list.remove("allow_blank=True")
    elif format == "time":
        field = "TimeField"
        example_string = "00:00:00"
        if not required:
            options_list.remove("allow_blank=True")
    # email, uuid not officially supported, mention we can use in swagger specs
    elif format == "email":
        field = "EmailField"
        example_string = "string@string.com"
        # if not required:
        #     options_list.remove("allow_blank=True")
    elif format == "uuid":
        field = "UUIDField"
        import uuid
        example_string = str(uuid.uuid4())
        if not required:
            options_list.remove("allow_blank=True")
    elif pattern:
        field = "RegexField"
        options_list_temp = [pattern]
        # print options_list_temp
        options_list_temp.extend(options_list)
        options_list = options_list_temp
        if not required:
            options_list.remove("allow_blank=True")
    elif enum:
        choices = ["('%s', '%s')" % (item, item) for item in enum]
        field = "ChoiceField"
        options_list_temp = ["choices=(%s)" % ", ".join(choices)]
        options_list_temp.extend(options_list)
        options_list = options_list_temp
        example_string = enum[0] if enum else example_string
        # if not required:
        #     options_list.remove("allow_blank=True")

    # URLField not supported by swagger 2.0
    # allow_blank not supported in swaggers specs
    # allow null not supported in swagger specs follow this issue
    # https://github.com/OAI/OpenAPI-Specification/issues/229
    if field == "RegexField":
        options = "regex = r'^" + "".join(options_list) + "$',required=True"
        char_field = 'serializers.%s(%s)' % (field, options)
    else:
        char_field = 'serializers.%s(%s)' % (
        field, str(", ".join(options_list)))
    if return_example:
        default = default if default else example_string
        return char_field, default
    return char_field
