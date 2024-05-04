import win32api


def get_first_resource_language(module: int, resource_type: int, resource_name: int) -> bytes:
    for resource_language_id in win32api.EnumResourceLanguages(module, resource_type, resource_name):
        return win32api.LoadResource(module, resource_type, resource_name, resource_language_id)
