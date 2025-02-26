from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QTableWidgetItem, QPushButton, QProgressBar,
                            QLabel, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import wmi
import pythoncom
from datetime import datetime
import os
import subprocess
from ...utils.logger import get_logger
from .base_tab import BaseTab
from ...utils.i18n import _

logger = get_logger(__name__)

class UpdatesWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def run(self):
        pythoncom.CoInitialize()
        try:
            c = wmi.WMI()
            updates = []
            
            for update in c.Win32_QuickFixEngineering():
                # Formata a data de instalação
                install_date = update.InstalledOn
                if install_date:
                    try:
                        date_obj = datetime.strptime(str(install_date), '%m/%d/%Y')
                        formatted_date = date_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        formatted_date = str(install_date)
                else:
                    formatted_date = _("updates.not_available")
                
                updates.append({
                    'kb': update.HotFixID or _("updates.not_available"),
                    'description': update.Description or _("updates.not_available"),
                    'date': formatted_date
                })
            
            # Ordena as atualizações por data (mais recentes primeiro)
            updates.sort(key=lambda x: x['date'], reverse=True)
            self.finished.emit(updates)
            
        except Exception as e:
            logger.error(f"Erro ao listar atualizações: {e}")
            self.error.emit(str(e))
        finally:
            pythoncom.CoUninitialize()

class UpdatesTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Remove o layout antigo se existir
        if self.layout():
            QWidget().setLayout(self.layout())
            
        layout = QVBoxLayout()
        
        # Status e Progresso
        self.status_label = QLabel()
        self.set_translation_key(self.status_label, "updates.status_ready")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Tabela de Atualizações
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            _("updates.kb"),
            _("updates.description"),
            _("updates.install_date")
        ])
        
        # Configura a tabela
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.check_button = QPushButton()
        self.set_translation_key(self.check_button, "updates.check")
        self.check_button.clicked.connect(self.check_updates)
        button_layout.addWidget(self.check_button)
        
        self.install_button = QPushButton()
        self.set_translation_key(self.install_button, "updates.install")
        self.install_button.clicked.connect(self.install_updates)
        self.install_button.setEnabled(False)
        button_layout.addWidget(self.install_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.update_translations()
        
    def check_updates(self):
        """Verifica atualizações instaladas"""
        try:
            self.status_label.setText(_("updates.status_checking"))
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Modo indeterminado
            self.check_button.setEnabled(False)
            self.install_button.setEnabled(False)
            self.table.setRowCount(0)
            
            self.worker = UpdatesWorker()
            self.worker.finished.connect(self.update_table)
            self.worker.error.connect(self.handle_error)
            self.worker.start()
            
        except Exception as e:
            logger.error(f"Erro ao verificar atualizações: {e}")
            self.handle_error(str(e))
        
    def update_table(self, updates):
        """Atualiza a tabela com as atualizações encontradas"""
        try:
            self.table.setRowCount(0)  # Limpa a tabela
            
            for update in updates:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # KB
                kb_item = QTableWidgetItem(update['kb'])
                kb_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, kb_item)
                
                # Descrição
                desc_item = QTableWidgetItem(update['description'])
                desc_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, 1, desc_item)
                
                # Data
                date_item = QTableWidgetItem(update['date'])
                date_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 2, date_item)
            
            # Atualiza status
            self.status_label.setText(_("updates.status_found").format(count=len(updates)))
            self.progress_bar.setVisible(False)
            self.check_button.setEnabled(True)
            self.install_button.setEnabled(True)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar tabela: {e}")
            self.handle_error(str(e))
        
    def handle_error(self, error_msg):
        """Trata erros na verificação de atualizações"""
        self.status_label.setText(_("updates.status_error").format(error=error_msg))
        self.progress_bar.setVisible(False)
        self.check_button.setEnabled(True)
        self.install_button.setEnabled(False)
        
        QMessageBox.warning(
            self,
            _("status.error"),
            _("updates.status_error").format(error=error_msg)
        )
        
    def install_updates(self):
        """Abre as configurações do Windows Update"""
        try:
            # Tenta abrir usando o comando moderno
            subprocess.Popen(['start', 'ms-settings:windowsupdate'], shell=True)
        except Exception as e1:
            logger.warning(f"Erro ao abrir configurações modernas: {e1}")
            try:
                # Fallback para o método antigo
                os.system('control update')
            except Exception as e2:
                logger.error(f"Erro ao abrir Windows Update: {e2}")
                QMessageBox.warning(
                    self,
                    _("status.error"),
                    str(e2)
                )
                
    def closeEvent(self, event):
        """Garante que o worker seja finalizado"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept() 