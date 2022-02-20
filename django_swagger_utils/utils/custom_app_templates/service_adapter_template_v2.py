service_adapter_template_v2 = """{% autoescape off %}class ServiceAdapter:

    @property
    def users(self):
        from .user_service_adapter import UserServiceAdapter
        return UserServiceAdapter()


def get_service_adapter():
    return ServiceAdapter()

{% endautoescape %}"""
