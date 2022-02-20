service_adapter_template_v3 = """{% autoescape off %}class ServiceAdapter:
    pass


def get_service_adapter():
    return ServiceAdapter()

{% endautoescape %}"""
