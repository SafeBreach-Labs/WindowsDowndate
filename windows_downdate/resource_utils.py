import win32api


def get_first_resource_language(module: int, resource_type: int, resource_name: int) -> bytes:
    """
    Gets the first resource language of a module via EnumResourceLanguages and LoadResource

    :param module: Module handle, can be retrieved via LoadLibrary or GetModuleHandle
    :param resource_type: Resource type - module specific information
    :param resource_name: Resource name - module specific information
    :return: The bytes of the first resource language found
    """
    for resource_language_id in win32api.EnumResourceLanguages(module, resource_type, resource_name):
        return win32api.LoadResource(module, resource_type, resource_name, resource_language_id)
