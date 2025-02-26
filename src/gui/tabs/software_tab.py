from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QLineEdit,
                               QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import winreg
import os
import psutil
from win32com.client import Dispatch
from ...utils.logger import get_logger
from .base_tab import BaseTab
from ...utils.i18n import _

logger = get_logger(__name__)

class SoftwareScanner(QThread):
    software_found = pyqtSignal(dict)
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    
    def run(self):
        """Escaneia software instalado no sistema"""
        try:
            software_list = {}
            
            # Verifica registros do Windows (32 e 64 bits)
            self.progress.emit(0, _("software.checking_registries"))
            paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]
            
            total_paths = len(paths)
            for i, (hkey, key_path) in enumerate(paths):
                try:
                    key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                    
                    # Conta subchaves para progresso
                    try:
                        num_subkeys = winreg.QueryInfoKey(key)[0]
                    except:
                        num_subkeys = 0
                    
                    for j in range(num_subkeys):
                        try:
                            subkey_name = winreg.EnumKey(key, j)
                            subkey = winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                            
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                
                                # Ignora entradas sem nome
                                if not name:
                                    continue
                                
                                # Coleta informações
                                info = {
                                    'name': name,
                                    'publisher': winreg.QueryValueEx(subkey, "Publisher")[0] if self._has_value(subkey, "Publisher") else "N/A",
                                    'version': winreg.QueryValueEx(subkey, "DisplayVersion")[0] if self._has_value(subkey, "DisplayVersion") else "N/A",
                                    'install_date': winreg.QueryValueEx(subkey, "InstallDate")[0] if self._has_value(subkey, "InstallDate") else "N/A",
                                    'size': winreg.QueryValueEx(subkey, "EstimatedSize")[0] if self._has_value(subkey, "EstimatedSize") else 0,
                                    'uninstall': winreg.QueryValueEx(subkey, "UninstallString")[0] if self._has_value(subkey, "UninstallString") else None
                                }
                                
                                # Adiciona à lista
                                software_list[name] = info
                                
                            except WindowsError:
                                # Ignora entradas inválidas
                                pass
                            except Exception as e:
                                logger.warning(f"Erro ao ler informações do software: {e}")
                                
                            finally:
                                try:
                                    winreg.CloseKey(subkey)
                                except:
                                    pass
                                
                            # Atualiza progresso
                            progress = int(((i * num_subkeys + j) / (total_paths * num_subkeys)) * 100)
                            self.progress.emit(progress, _("software.scanning_installed").format(found=len(software_list)))
                            
                        except WindowsError:
                            # Ignora subchaves inválidas
                            pass
                        except Exception as e:
                            logger.warning(f"Erro ao enumerar subchave: {e}")
                            
                    try:
                        winreg.CloseKey(key)
                    except:
                        pass
                    
                except WindowsError:
                    # Ignora chaves não encontradas
                    pass
                except Exception as e:
                    logger.error(f"Erro ao abrir chave {key_path}: {e}")
            
            # Verifica Microsoft Store apps
            self.progress.emit(90, _("software.checking_store_apps"))
            try:
                powershell_command = "pwsh -Command \"Get-AppxPackage | Select-Object Name,Publisher,Version,InstallLocation\""
                with os.popen(powershell_command) as p:
                    for line in p:
                        try:
                            if line.strip() and not line.startswith("Name"):
                                parts = line.strip().split()
                                if len(parts) >= 3:
                                    name = parts[0]
                                    info = {
                                        'name': name,
                                        'publisher': parts[1],
                                        'version': parts[2],
                                        'install_date': "N/A",
                                        'size': 0,
                                        'uninstall': None,
                                        'store_app': True
                                    }
                                    software_list[name] = info
                        except Exception as e:
                            logger.warning(f"Erro ao processar app da Store: {e}")
                            
            except Exception as e:
                logger.error(f"Erro ao verificar apps da Store: {e}")
            
            # Emite lista completa
            self.software_found.emit(software_list)
            
        except Exception as e:
            logger.error(f"Erro ao escanear software: {e}")
            
        finally:
            self.progress.emit(100, _("software.scan_finished"))
            self.finished.emit()
    
    def _has_value(self, key, value_name):
        """Verifica se uma chave do registro tem um valor específico"""
        try:
            winreg.QueryValueEx(key, value_name)
            return True
        except:
            return False

class SoftwareTab(BaseTab):
    def __init__(self):
        self.software_list = {}
        super().__init__()
        self.setup_ui()
        self.scan_software()
        
    def setup_ui(self):
        # Remove o layout antigo se existir
        if self.layout():
            QWidget().setLayout(self.layout())
            
        layout = QVBoxLayout()
        
        # Barra de pesquisa
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.set_placeholder_key(self.search_input, "software.search_placeholder")
        self.search_input.textChanged.connect(self.filter_software)
        search_layout.addWidget(self.search_input)
        
        self.scan_button = QPushButton()
        self.set_translation_key(self.scan_button, "software.refresh")
        self.scan_button.clicked.connect(self.scan_software)
        search_layout.addWidget(self.scan_button)
        
        layout.addLayout(search_layout)
        
        # Status
        self.status_label = QLabel()
        self.set_translation_key(self.status_label, "software.loading")
        layout.addWidget(self.status_label)
        
        # Tabela de software
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            _("software.name"),
            _("software.publisher"),
            _("software.version"),
            _("software.install_date"),
            _("software.size")
        ])
        
        # Configura a tabela
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemDoubleClicked.connect(self.show_software_details)
        
        layout.addWidget(self.table)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.uninstall_button = QPushButton()
        self.set_translation_key(self.uninstall_button, "software.uninstall")
        self.uninstall_button.clicked.connect(self.uninstall_software)
        self.uninstall_button.setEnabled(False)
        button_layout.addWidget(self.uninstall_button)
        
        self.repair_button = QPushButton()
        self.set_translation_key(self.repair_button, "software.repair")
        self.repair_button.clicked.connect(self.repair_software)
        self.repair_button.setEnabled(False)
        button_layout.addWidget(self.repair_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.update_translations()
        
    def scan_software(self):
        """Inicia o escaneamento de software"""
        try:
            self.scan_button.setEnabled(False)
            self.status_label.setText(_("software.scanning"))
            
            self.scanner = SoftwareScanner()
            self.scanner.software_found.connect(self.update_software_list)
            self.scanner.progress.connect(self.update_progress)
            self.scanner.finished.connect(self.scan_finished)
            self.scanner.start()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar escaneamento: {e}")
            self.status_label.setText(_("software.scan_error"))
            self.scan_button.setEnabled(True)
            
    def update_software_list(self, software_list):
        """Atualiza a lista de software"""
        try:
            self.software_list = software_list
            self.filter_software()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar lista: {e}")
            
    def update_progress(self, value, status):
        """Atualiza o progresso do escaneamento"""
        self.status_label.setText(status)
        
    def scan_finished(self):
        """Chamado quando o escaneamento é concluído"""
        try:
            self.scan_button.setEnabled(True)
            self.status_label.setText(_("software.total_found").format(total=len(self.software_list)))
            
        except Exception as e:
            logger.error(f"Erro ao finalizar escaneamento: {e}")
            
    def filter_software(self):
        """Filtra a lista de software baseado na pesquisa"""
        try:
            search_text = self.search_input.text().lower()
            
            # Limpa a tabela
            self.table.setRowCount(0)
            
            # Adiciona software filtrado
            for name, info in self.software_list.items():
                if search_text in name.lower() or search_text in info['publisher'].lower():
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    
                    # Nome
                    self.table.setItem(row, 0, QTableWidgetItem(info['name']))
                    
                    # Publicador
                    self.table.setItem(row, 1, QTableWidgetItem(info['publisher']))
                    
                    # Versão
                    self.table.setItem(row, 2, QTableWidgetItem(info['version']))
                    
                    # Data de instalação
                    self.table.setItem(row, 3, QTableWidgetItem(info['install_date']))
                    
                    # Tamanho
                    size = info['size']
                    if size > 0:
                        size_mb = size / 1024  # KB para MB
                        size_text = f"{size_mb:.1f} MB"
                    else:
                        size_text = _("software.unknown_size")
                    self.table.setItem(row, 4, QTableWidgetItem(size_text))
            
            # Atualiza botões
            self.update_buttons()
            
        except Exception as e:
            logger.error(f"Erro ao filtrar software: {e}")
            
    def update_buttons(self):
        """Atualiza estado dos botões baseado na seleção"""
        try:
            selected = len(self.table.selectedItems()) > 0
            self.uninstall_button.setEnabled(selected)
            self.repair_button.setEnabled(selected)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar botões: {e}")
            
    def show_software_details(self, item):
        """Mostra detalhes do software selecionado"""
        try:
            row = item.row()
            name = self.table.item(row, 0).text()
            info = self.software_list.get(name)
            
            if info:
                msg = QMessageBox()
                msg.setWindowTitle(_("software.details_title"))
                msg.setText(info['name'])
                
                details = f"{_('software.publisher')}: {info['publisher']}\n"
                details += f"{_('software.version')}: {info['version']}\n"
                details += f"{_('software.install_date')}: {info['install_date']}\n"
                
                size = info['size']
                if size > 0:
                    size_mb = size / 1024  # KB para MB
                    details += f"{_('software.size')}: {size_mb:.1f} MB\n"
                else:
                    details += f"{_('software.size')}: {_('software.unknown_size')}\n"
                
                msg.setDetailedText(details)
                msg.exec_()
                
        except Exception as e:
            logger.error(f"Erro ao mostrar detalhes: {e}")
            
    def uninstall_software(self):
        """Desinstala o software selecionado"""
        try:
            row = self.table.currentRow()
            if row >= 0:
                name = self.table.item(row, 0).text()
                info = self.software_list.get(name)
                
                if info:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle(_("software.uninstall_title"))
                    msg.setText(_("software.confirm_uninstall").format(name=name))
                    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    
                    if msg.exec_() == QMessageBox.Yes:
                        uninstall_cmd = info.get('uninstall')
                        if uninstall_cmd:
                            os.system(f'start "" "{uninstall_cmd}"')
                        else:
                            QMessageBox.warning(
                                self,
                                _("status.error"),
                                _("software.no_uninstall")
                            )
                
        except Exception as e:
            logger.error(f"Erro ao desinstalar: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("software.uninstall_error").format(error=str(e))
            )
            
    def repair_software(self):
        """Tenta reparar o software selecionado"""
        try:
            row = self.table.currentRow()
            if row >= 0:
                name = self.table.item(row, 0).text()
                info = self.software_list.get(name)
                
                if info:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Question)
                    msg.setWindowTitle(_("software.repair_title"))
                    msg.setText(_("software.confirm_repair").format(name=name))
                    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    
                    if msg.exec_() == QMessageBox.Yes:
                        # Tenta reparar usando diferentes métodos
                        methods = [
                            self._repair_using_installer,
                            self._repair_using_dism,
                            self._repair_using_sfc
                        ]
                        
                        repaired = False
                        for method in methods:
                            if method(info):
                                repaired = True
                                break
                        
                        if not repaired:
                            QMessageBox.warning(
                                self,
                                _("status.error"),
                                _("software.repair_failed")
                            )
                
        except Exception as e:
            logger.error(f"Erro ao reparar: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("software.repair_error").format(error=str(e))
            )
            
    def _repair_using_installer(self, info):
        """Tenta reparar usando o instalador original"""
        try:
            uninstall_cmd = info.get('uninstall', '')
            if '/repair' in uninstall_cmd.lower():
                os.system(f'start "" "{uninstall_cmd} /repair"')
                return True
        except:
            pass
        return False
    
    def _repair_using_dism(self, info):
        """Tenta reparar usando DISM (Windows)"""
        try:
            if 'Microsoft' in info['publisher']:
                os.system('DISM /Online /Cleanup-Image /RestoreHealth')
                return True
        except:
            pass
        return False
    
    def _repair_using_sfc(self, info):
        """Tenta reparar usando SFC (Windows)"""
        try:
            if 'Microsoft' in info['publisher']:
                os.system('sfc /scannow')
                return True
        except:
            pass
        return False

    def closeEvent(self, event):
        """Garante que o scanner seja finalizado"""
        if hasattr(self, 'scanner') and self.scanner.isRunning():
            self.scanner.terminate()
            self.scanner.wait()
            
        event.accept() 