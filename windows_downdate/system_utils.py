import win32api


def initiate_system_shutdown(computer_name: str,
                             message: str = "",
                             timeout: int = 0,
                             force_close: int = 0,
                             reboot_after_shutdown: int = 1) -> None:
    win32api.InitiateSystemShutdown(computer_name, message, timeout, force_close, reboot_after_shutdown)


def restart_system(timeout: int = 0) -> None:
    initiate_system_shutdown("127.0.0.1", timeout=timeout, force_close=1, reboot_after_shutdown=1)
