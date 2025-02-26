from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout,
                            QLabel, QFrame, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from ...utils.system_info import SystemInfo
from ...utils.styles import StyleSheet
from .base_tab import BaseTab
from ...utils.i18n import _

class MonitoringTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.system_info = SystemInfo()
        self.setup_ui()
        self.start_monitoring()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Grid para os cards de métricas
        grid = QGridLayout()
        layout.addLayout(grid)
        
        # CPU Card
        self.cpu_card = self.create_metric_card(_("monitoring.cpu"), "0%")
        grid.addWidget(self.cpu_card, 0, 0)
        
        # RAM Card
        self.ram_card = self.create_metric_card(_("monitoring.ram"), "0%")
        grid.addWidget(self.ram_card, 0, 1)
        
        # Disco Card
        self.disk_card = self.create_metric_card(_("monitoring.disk"), "0%")
        grid.addWidget(self.disk_card, 1, 0)
        
        # GPU Card
        self.gpu_card = self.create_metric_card(_("monitoring.gpu"), "0%")
        grid.addWidget(self.gpu_card, 1, 1)
        
        # Aplicar estilos
        self.setStyleSheet(StyleSheet.MONITORING_TAB)
        
        self.setLayout(layout)
        
    def create_metric_card(self, title, initial_value):
        card = QFrame()
        card.setProperty("class", "metric-card")
        
        layout = QVBoxLayout(card)
        
        # Título
        title_label = QLabel(title)
        title_label.setProperty("class", "metric-title")
        layout.addWidget(title_label)
        
        # Valor
        value_label = QLabel(initial_value)
        value_label.setProperty("class", "metric-value")
        layout.addWidget(value_label)
        
        # Barra de progresso
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        layout.addWidget(progress)
        
        # Armazena referências
        card.title_label = title_label
        card.value_label = value_label
        card.progress = progress
        
        return card
        
    def start_monitoring(self):
        """Inicia o monitoramento em tempo real"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # Atualiza a cada segundo
        
    def update_metrics(self):
        """Atualiza as métricas em tempo real"""
        try:
            metrics = self.system_info.get_performance_metrics()
            
            # Atualiza CPU
            self.update_card(self.cpu_card, 
                           f"{metrics['cpu_percent']:.1f}%",
                           metrics['cpu_percent'])
            
            # Atualiza RAM
            self.update_card(self.ram_card,
                           f"{metrics['ram_percent']:.1f}%",
                           metrics['ram_percent'])
            
            # Atualiza Disco
            self.update_card(self.disk_card,
                           f"{metrics['disk_percent']:.1f}%",
                           metrics['disk_percent'])
            
            # Atualiza GPU
            self.update_card(self.gpu_card,
                           f"{metrics['gpu_load']:.1f}%",
                           metrics['gpu_load'])
            
        except Exception as e:
            print(_("monitoring.error").format(error=str(e)))
            
    def update_card(self, card, value_text, progress_value):
        """Atualiza um card de métrica"""
        card.value_label.setText(value_text)
        card.progress.setValue(int(progress_value))
        
        # Atualiza cor baseado no valor
        if progress_value > 90:
            card.progress.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        elif progress_value > 70:
            card.progress.setStyleSheet("QProgressBar::chunk { background-color: #f1c40f; }")
        else:
            card.progress.setStyleSheet("QProgressBar::chunk { background-color: #2ecc71; }")
            
    def update_translations(self):
        """Atualiza as traduções da interface"""
        self.cpu_card.title_label.setText(_("monitoring.cpu"))
        self.ram_card.title_label.setText(_("monitoring.ram"))
        self.disk_card.title_label.setText(_("monitoring.disk"))
        self.gpu_card.title_label.setText(_("monitoring.gpu"))
            
    def closeEvent(self, event):
        """Para o timer quando a aba é fechada"""
        self.timer.stop()
        super().closeEvent(event) 