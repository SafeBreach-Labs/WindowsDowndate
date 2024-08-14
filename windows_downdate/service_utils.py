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
    """
    Represents service status data container
    """
    service_type: int
    current_state: int
    controls_accepted: int
    win32_exit_code: int
    service_specific_exit_code: int
    check_point: int
    wait_hing: int


# TODO: Finalize docs
def set_service_start_type(service_name: str, start_type: int) -> None:
    """
    Sets service start type given service name

    :param service_name: The name of the service to change its start type
    :param start_type: The start type to set. Can be one of the following -
    :return: None
    """
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
    """
    Queries service status by service name

    :param service_name: The name of the service to get its status
    :return: Initialized ServiceStatus data container
    """
    service_status = win32serviceutil.QueryServiceStatus(service_name)
    return ServiceStatus(*service_status)


def wait_for_service_to_leave_pending_state(service_name: str) -> ServiceStatus:
    """
    Waits for service to leave pending state
    Pending states -
            SERVICE_START_PENDING
            SERVICE_STOP_PENDING,
            SERVICE_CONTINUE_PENDING
            SERVICE_PAUSE_PENDING

    :param service_name: The name of the service to wait until it leaves pending state
    :return: Initialized ServiceStatus data container
    :raises: Exception - if service is in pending state for too long
    :note: The API sleeps 10 seconds between each query, and queries maximum of 10 times
    """
    retry_counter = 0
    service_status = query_service_status(service_name)

    while service_status.current_state in SERVICE_PENDING_STATES:
        retry_counter += 1
        if retry_counter > PENDING_STATES_QUERY_RETRIES:
            raise Exception(f"Service {service_name} is in pending state {service_status.current_state} for too long")
        time.sleep(WAIT_BEFORE_NEXT_QUERY_RETRY)
        service_status = query_service_status(service_name)

    return service_status


def start_service(service_name: str, service_args: List[Any] = None, resume_if_paused: bool = True) -> None:
    """
    Starts a service given service name

    :param service_name: The name of the service to start
    :param service_args: List of arguments to run the service with
    :param resume_if_paused: Flag indicating if to resume the service if it is in paused sate
    :return: None
    :raises: Exception - when unexpected service state occurs
    :note: If the process is already running, the API does nothing
    """
    service_status = wait_for_service_to_leave_pending_state(service_name)

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
