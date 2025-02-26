import platform
import psutil
import wmi
import socket
import uuid
import win32net
import win32api
import GPUtil
from datetime import datetime
from .logger import get_logger

logger = get_logger(__name__)

class SystemInfo:
    def __init__(self):
        try:
            self.wmi = wmi.WMI()
        except Exception as e:
            logger.error(f"Erro ao inicializar WMI: {e}")
            self.wmi = None
        
    def get_all_info(self):
        """Obtém todas as informações do sistema"""
        try:
            info = {}
            info.update(self.get_hardware_info())
            info.update(self.get_os_info())
            info.update(self.get_network_info())
            return info
        except Exception as e:
            logger.error(f"Erro ao obter informações do sistema: {e}")
            return {}
        
    def get_hardware_info(self):
        """Obtém informações do hardware"""
        try:
            # CPU
            cpu_info = {}
            if self.wmi:
                cpu = self.wmi.Win32_Processor()[0]
                cpu_info = f"{cpu.Name} ({cpu.NumberOfCores} núcleos)"
            else:
                cpu_info = platform.processor()
            
            # RAM
            ram = psutil.virtual_memory()
            ram_total = round(ram.total / (1024**3))
            ram_used = round(ram.used / (1024**3))
            ram_info = f"{ram_used}GB / {ram_total}GB ({ram.percent}%)"
            
            # Disco
            disk = psutil.disk_usage('C:\\')
            disk_total = round(disk.total / (1024**3))
            disk_used = round(disk.used / (1024**3))
            disk_info = f"{disk_used}GB / {disk_total}GB ({disk.percent}%)"
            
            # GPU
            try:
                gpus = GPUtil.getGPUs()
                gpu = gpus[0].name if gpus else "GPU não encontrada"
            except:
                gpu = "Não foi possível obter informações da GPU"
                
            return {
                'cpu': cpu_info,
                'ram': ram_info,
                'disk': disk_info,
                'gpu': gpu
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações de hardware: {e}")
            return {
                'cpu': 'N/A',
                'ram': 'N/A',
                'disk': 'N/A',
                'gpu': 'N/A'
            }
        
    def get_os_info(self):
        """Obtém informações do sistema operacional"""
        try:
            os_info = {
                'os': platform.system(),
                'version': platform.version(),
                'arch': platform.architecture()[0],
                'hostname': platform.node()
            }
            
            if self.wmi:
                try:
                    computer = self.wmi.Win32_ComputerSystem()[0]
                    os_info['manufacturer'] = computer.Manufacturer
                    os_info['model'] = computer.Model
                except:
                    os_info['manufacturer'] = "Não disponível"
                    os_info['model'] = "Não disponível"
                    
            return os_info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do sistema operacional: {e}")
            return {
                'os': 'N/A',
                'version': 'N/A',
                'arch': 'N/A',
                'hostname': 'N/A'
            }
        
    def get_network_info(self):
        """Obtém informações de rede"""
        try:
            # IP
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            # MAC
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0,2*6,2)][::-1])
            
            # DNS e Gateway
            dns_servers = []
            gateway = "Não disponível"
            
            if self.wmi:
                try:
                    nic_config = self.wmi.Win32_NetworkAdapterConfiguration(IPEnabled=True)
                    for nic in nic_config:
                        if nic.DNSServerSearchOrder:
                            dns_servers.extend(nic.DNSServerSearchOrder)
                        if nic.DefaultIPGateway:
                            gateway = nic.DefaultIPGateway[0]
                            break
                except Exception as e:
                    logger.error(f"Erro ao obter configurações de rede: {e}")
            
            dns = ', '.join(set(dns_servers)) if dns_servers else "Não disponível"
                    
            return {
                'ip': ip,
                'mac': mac.upper(),
                'dns': dns,
                'gateway': gateway
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações de rede: {e}")
            return {
                'ip': 'N/A',
                'mac': 'N/A',
                'dns': 'N/A',
                'gateway': 'N/A'
            }
        
    def get_performance_metrics(self):
        """Obtém métricas de desempenho em tempo real"""
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        
        try:
            gpus = GPUtil.getGPUs()
            gpu_load = gpus[0].load * 100 if gpus else 0
            gpu_memory = gpus[0].memoryUtil * 100 if gpus else 0
        except:
            gpu_load = 0
            gpu_memory = 0
            
        return {
            'cpu_percent': cpu_percent,
            'ram_percent': ram.percent,
            'disk_percent': disk.percent,
            'gpu_load': gpu_load,
            'gpu_memory': gpu_memory
        }
        
    def get_system_health(self):
        """Avalia a saúde do sistema"""
        metrics = self.get_performance_metrics()
        health_status = {
            'status': 'Bom',
            'issues': []
        }
        
        # Verifica CPU
        if metrics['cpu_percent'] > 90:
            health_status['issues'].append("CPU com uso muito alto")
            health_status['status'] = 'Atenção'
            
        # Verifica RAM
        if metrics['ram_percent'] > 90:
            health_status['issues'].append("Memória RAM próxima do limite")
            health_status['status'] = 'Atenção'
            
        # Verifica Disco
        if metrics['disk_percent'] > 90:
            health_status['issues'].append("Disco próximo do limite")
            health_status['status'] = 'Atenção'
            
        # Verifica temperatura (se disponível)
        try:
            temperatures = psutil.sensors_temperatures()
            for name, entries in temperatures.items():
                for entry in entries:
                    if entry.current > 80:  # temperatura em Celsius
                        health_status['issues'].append(f"Temperatura alta: {name}")
                        health_status['status'] = 'Atenção'
        except:
            pass
            
        return health_status 