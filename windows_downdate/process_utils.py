import psutil


def get_process_by_name(process_name: str) -> int:
    for proc_info in psutil.process_iter(['pid', 'name']):
        if proc_info.name().lower() == process_name.lower():
            return proc_info.pid
