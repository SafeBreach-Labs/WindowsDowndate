import psutil


def get_process_id_by_name(process_name: str) -> int:
    """
    Gets process ID by process name

    :param process_name:
    :return: The first process ID that has name of process_name
    :raises: Exception - if did not find any process with name process_name
    """
    for proc_info in psutil.process_iter(['pid', 'name']):
        if proc_info.name().lower() == process_name.lower():
            return proc_info.pid
    raise Exception(f"Process {process_name} is not running")
