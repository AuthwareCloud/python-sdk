import wmi

from authware.cryptography import Cryptography

class HardwareId:
    crypto = Cryptography()

    def get_cpu_id(self):
        wql = "Select ProcessorId From Win32_processor"
        id = None
        for id in wmi.WMI().query(wql):
            id = str(id)
            
        return id
    
    def get_id(self):
        cpu_id = self.get_cpu_id()
        
        return self.crypto.hash_sha256(cpu_id)