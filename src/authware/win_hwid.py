import wmi

from .hwid import HardwareId
from .cryptography import hash_sha256


def get_cpu_id():
    wql = "Select ProcessorId From Win32_processor"
    cpu_id = None
    for cpu_id in wmi.WMI().query(wql):
        cpu_id = str(cpu_id)

    return cpu_id


class WindowsHardwareId(HardwareId):

    def get_id(self):
        cpu_id = get_cpu_id()

        return hash_sha256(cpu_id)
