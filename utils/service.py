import win32service


def set_service_start_type(service_name: str, start_type: int) -> None:
    sc_manager_handle = win32service.OpenSCManager(None, None, win32service.SERVICE_CHANGE_CONFIG)
    service_handle = win32service.OpenService(sc_manager_handle, service_name, win32service.SERVICE_CHANGE_CONFIG)
    win32service.ChangeServiceConfig(
        service_handle,
        win32service.SERVICE_NO_CHANGE,
        start_type,
        win32service.SERVICE_NO_CHANGE,
        None,
        None,
        None,
        None,
        None,
        None,
        None
    )


def set_service_auto_start(service_name: str) -> None:
    set_service_start_type(service_name, win32service.SERVICE_AUTO_START)
