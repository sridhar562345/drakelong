user_service_adapter_template = """{% autoescape off %}class UserServiceAdapter:

    @property
    def interface(self):
        # from ib_users.interfaces.service_interface import ServiceInterface
        # return ServiceInterface()
        return

    def get_user_id_from_username(self, username: str) -> str:
        user_id = self.interface.get_user_from_username(username)
        return user_id

{% endautoescape %}"""
