import time
from dataclasses import dataclass
from typing import List, Any

import win32service
import win32serviceutil


SERVICE_PENDING_STATES = [win32service.SERVICE_START_PENDING, win32service.SERVICE_STOP_PENDING,
                          win32service.SERVICE_CONTINUE_PENDING, win32service.SERVICE_PAUSE_PENDING]

PENDING_STATES_QUERY_RETRIES = 10

WAIT_BEFORE_NEXT_QUERY_RETRY = 10.0

WAIT_FOR_STATUS_TIMEOUT = 20


@dataclass
class ServiceStatus:
    service_type: int
    current_state: int
    controls_accepted: int
    win32_exit_code: int
    service_specific_exit_code: int
    check_point: int
    wait_hing: int


# TODO: Consider using win32serviceutil.ChangeServiceConfig instead of win32service.ChangeServiceConfig
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
        False,
        None,
        None,
        None,
        None
    )


def query_service_status(service_name: str) -> ServiceStatus:
    service_status = win32serviceutil.QueryServiceStatus(service_name)
    return ServiceStatus(*service_status)


def start_service(service_name: str, service_args: List[Any] = None, resume_if_paused: bool = True) -> None:
    service_status = query_service_status(service_name)

    retry_counter = 0
    while service_status.current_state in SERVICE_PENDING_STATES:
        retry_counter += 1
        if retry_counter > PENDING_STATES_QUERY_RETRIES:
            raise Exception(f"Service {service_name} is in pending state {service_status.current_state} for too long")
        time.sleep(WAIT_BEFORE_NEXT_QUERY_RETRY)
        service_status = query_service_status(service_name)

    if service_status.current_state == win32service.SERVICE_RUNNING:
        return

    elif service_status.current_state == win32service.SERVICE_PAUSED:
        if resume_if_paused:
            win32serviceutil.ControlService(service_name, win32service.SERVICE_CONTROL_CONTINUE)
        else:
            return

    elif service_status.current_state == win32service.SERVICE_STOPPED:
        win32serviceutil.StartService(service_name, service_args)

    else:
        raise Exception(f"Unexpected service state: {service_status.current_state}")

    win32serviceutil.WaitForServiceStatus(service_name, win32service.SERVICE_RUNNING, WAIT_FOR_STATUS_TIMEOUT)
