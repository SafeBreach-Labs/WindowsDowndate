import psutil


def get_process_id_by_name(process_name: str) -> int:
    for proc_info in psutil.process_iter(['pid', 'name']):
        if proc_info.name().lower() == process_name.lower():
            return proc_info.pid
    raise Exception(f"Process {process_name} is not running")
