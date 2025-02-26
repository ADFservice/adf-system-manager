from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QGroupBox, QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
import psutil
import GPUtil
import platform
import wmi
import pythoncom
from ...utils.logger import get_logger
from .base_tab import BaseTab
from ...utils.i18n import _

logger = get_logger(__name__)

class SystemInfoWorker(QThread):
    info_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        # Inicializa COM para esta thread
        pythoncom.CoInitialize()
        
        try:
            # Conecta ao WMI
            self.wmi = wmi.WMI()
            
            while self.running:
                try:
                    info = self.get_system_info()
                    self.info_updated.emit(info)
                except Exception as e:
                    logger.error(f"Erro ao obter informações do sistema: {e}")
                
                # Aguarda 1 segundo
                self.sleep(1)
                
        finally:
            # Finaliza COM
            pythoncom.CoUninitialize()
            
    def stop(self):
        self.running = False
        
    def get_system_info(self):
        """Obtém informações do sistema"""
        info = {}
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_freq = psutil.cpu_freq()
            cpu_info = self.wmi.Win32_Processor()[0]
            
            info['cpu'] = {
                'name': cpu_info.Name,
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(),
                'usage': cpu_percent,
                'freq': f"{cpu_freq.current:.0f} MHz"
            }
            
            # Memória
            mem = psutil.virtual_memory()
            info['memory'] = {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'percent': mem.percent
            }
            
            # GPU
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    info['gpu'] = {
                        'name': gpu.name,
                        'memory_total': gpu.memoryTotal,
                        'memory_used': gpu.memoryUsed,
                        'temperature': gpu.temperature,
                        'load': gpu.load * 100
                    }
            except Exception as e:
                logger.warning(f"Erro ao obter informações da GPU: {e}")
            
            # Disco
            disks = []
            for disk in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(disk.mountpoint)
                    disks.append({
                        'device': disk.device,
                        'mountpoint': disk.mountpoint,
                        'fstype': disk.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except Exception as e:
                    logger.warning(f"Erro ao obter informações do disco {disk.device}: {e}")
            
            info['disks'] = disks
            
            # Sistema Operacional
            os_info = platform.uname()
            info['os'] = {
                'system': os_info.system,
                'release': os_info.release,
                'version': os_info.version,
                'machine': os_info.machine,
                'processor': os_info.processor
            }
            
            # Rede
            net = psutil.net_io_counters()
            info['network'] = {
                'bytes_sent': net.bytes_sent,
                'bytes_recv': net.bytes_recv,
                'packets_sent': net.packets_sent,
                'packets_recv': net.packets_recv
            }
            
        except Exception as e:
            logger.error(f"Erro ao coletar informações do sistema: {e}")
            
        return info

class SystemTab(BaseTab):
    def __init__(self):
        self.system_info = {}  # Inicializa o dicionário de informações
        super().__init__()
        self.setup_ui()
        
        # Timer para atualização
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(2000)  # Atualiza a cada 2 segundos
        
        # Primeira atualização
        self.update_info()
        
    def setup_ui(self):
        # Remove o layout antigo se existir
        if self.layout():
            QWidget().setLayout(self.layout())
            
        # Layout principal
        main_layout = QVBoxLayout()
        
        # CPU
        cpu_group = QGroupBox()
        self.set_title_key(cpu_group, "system.cpu")
        cpu_layout = QVBoxLayout()
        
        self.cpu_usage_label = QLabel()
        self.set_translation_key(self.cpu_usage_label, "system.usage")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        
        cpu_layout.addWidget(self.cpu_usage_label)
        cpu_layout.addWidget(self.cpu_progress)
        cpu_group.setLayout(cpu_layout)
        main_layout.addWidget(cpu_group)
        
        # Memória
        memory_group = QGroupBox()
        self.set_title_key(memory_group, "system.memory")
        memory_layout = QVBoxLayout()
        
        self.memory_usage_label = QLabel()
        self.set_translation_key(self.memory_usage_label, "system.usage")
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        
        self.memory_total_label = QLabel()
        self.set_translation_key(self.memory_total_label, "system.total")
        self.memory_available_label = QLabel()
        self.set_translation_key(self.memory_available_label, "system.available")
        
        memory_layout.addWidget(self.memory_usage_label)
        memory_layout.addWidget(self.memory_progress)
        memory_layout.addWidget(self.memory_total_label)
        memory_layout.addWidget(self.memory_available_label)
        memory_group.setLayout(memory_layout)
        main_layout.addWidget(memory_group)
        
        # Disco
        disk_group = QGroupBox()
        self.set_title_key(disk_group, "system.disk")
        disk_layout = QVBoxLayout()
        
        self.disk_usage_label = QLabel()
        self.set_translation_key(self.disk_usage_label, "system.usage")
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        
        self.disk_total_label = QLabel()
        self.set_translation_key(self.disk_total_label, "system.total")
        self.disk_free_label = QLabel()
        self.set_translation_key(self.disk_free_label, "system.available")
        
        disk_layout.addWidget(self.disk_usage_label)
        disk_layout.addWidget(self.disk_progress)
        disk_layout.addWidget(self.disk_total_label)
        disk_layout.addWidget(self.disk_free_label)
        disk_group.setLayout(disk_layout)
        main_layout.addWidget(disk_group)
        
        self.setLayout(main_layout)
        self.update_translations()
    
    def update_info(self):
        try:
            # CPU
            cpu_percent = psutil.cpu_percent()
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_usage_label.setText(_("system.usage").format(value=cpu_percent))
            
            # Memória
            memory = psutil.virtual_memory()
            self.memory_progress.setValue(int(memory.percent))
            self.memory_usage_label.setText(_("system.usage").format(value=memory.percent))
            self.memory_total_label.setText(_("system.total").format(value=self.format_bytes(memory.total)))
            self.memory_available_label.setText(_("system.available").format(value=self.format_bytes(memory.available)))
            
            # Disco
            disk = psutil.disk_usage('/')
            self.disk_progress.setValue(int(disk.percent))
            self.disk_usage_label.setText(_("system.usage").format(value=disk.percent))
            self.disk_total_label.setText(_("system.total").format(value=self.format_bytes(disk.total)))
            self.disk_free_label.setText(_("system.free").format(value=self.format_bytes(disk.free)))
            
        except Exception as e:
            logger.error(f"Error updating system info: {str(e)}")
            self.cpu_usage_label.setText(_("system.loading"))
            self.memory_usage_label.setText(_("system.loading"))
            self.disk_usage_label.setText(_("system.loading"))

    def format_bytes(self, bytes):
        """Converte bytes para uma string formatada (KB, MB, GB)"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} PB"
    
    def closeEvent(self, event):
        """Para o worker quando a janela for fechada"""
        if hasattr(self, 'worker'):
            self.worker.stop()
            self.worker.wait()
        event.accept() 