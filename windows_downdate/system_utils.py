import win32api


def initiate_system_shutdown(computer_name: str,
                             message: str = "",
                             timeout: int = 0,
                             force_close: int = 0,
                             reboot_after_shutdown: int = 1) -> None:
    """
    Initiates system shutdown using InitiateSystemShutdown

    :param computer_name: The name of the computer to shut down
    :param message: Shutdown message
    :param timeout: Timeout to wait before shutdown
    :param force_close: Flag indicating if to force closing applications
    :param reboot_after_shutdown: Flag indicating if to reboot after shutdown
    :return: None
    """
    win32api.InitiateSystemShutdown(computer_name, message, timeout, force_close, reboot_after_shutdown)


def restart_system(timeout: int = 0) -> None:
    """
    Restart the local system with timeout

    :param timeout: Timeout to wait before restarting
    :return: None
    """
    initiate_system_shutdown("127.0.0.1", timeout=timeout, force_close=1, reboot_after_shutdown=1)
