import platform


def get_os_build_number() -> str:
    build_number = platform.version()
    if not build_number:
        raise Exception("Failed to retrieve build number")
    return build_number


def get_base_os_build_number() -> str:
    build_number = get_os_build_number()
    base_build_number = f"{build_number}.1"
    return base_build_number
