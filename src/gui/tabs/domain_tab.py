from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit,
                               QMessageBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import socket
import subprocess
import winreg
import os
import getpass
from ...utils.logger import get_logger
from .base_tab import BaseTab
from ...utils.i18n import _

logger = get_logger(__name__)

class DomainWorker(QThread):
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, action, **kwargs):
        super().__init__()
        self.action = action
        self.kwargs = kwargs
        
    def run(self):
        """Executa ações relacionadas ao domínio"""
        try:
            if self.action == "join":
                self._join_domain()
            elif self.action == "leave":
                self._leave_domain()
            elif self.action == "update":
                self._update_domain()
                
        except Exception as e:
            logger.error(f"Erro na operação de domínio: {e}")
            self.status_updated.emit(_("domain.error").format(error=str(e)))
            self.finished.emit(False)
    
    def _join_domain(self):
        """Adiciona o computador ao domínio"""
        try:
            domain = self.kwargs.get('domain')
            username = self.kwargs.get('username')
            password = self.kwargs.get('password')
            
            # Verifica se já está no domínio
            if self._is_domain_member():
                self.status_updated.emit(_("domain.already_member"))
                self.finished.emit(False)
                return
            
            # Comando para adicionar ao domínio
            cmd = [
                'powershell',
                '-Command',
                f'Add-Computer -DomainName "{domain}" -Credential (New-Object System.Management.Automation.PSCredential("{username}", (ConvertTo-SecureString "{password}" -AsPlainText -Force))) -Force -Restart'
            ]
            
            # Executa o comando
            self.status_updated.emit(_("domain.joining"))
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.status_updated.emit(_("domain.join_success"))
                self.finished.emit(True)
            else:
                error = result.stderr.strip()
                self.status_updated.emit(_("domain.join_error").format(error=error))
                self.finished.emit(False)
                
        except Exception as e:
            logger.error(f"Erro ao adicionar ao domínio: {e}")
            self.status_updated.emit(_("domain.join_error").format(error=str(e)))
            self.finished.emit(False)
    
    def _leave_domain(self):
        """Remove o computador do domínio"""
        try:
            # Verifica se está em um domínio
            if not self._is_domain_member():
                self.status_updated.emit(_("domain.not_member"))
                self.finished.emit(False)
                return
            
            # Comando para remover do domínio
            cmd = [
                'powershell',
                '-Command',
                'Remove-Computer -UnjoinDomainCredential (Get-Credential) -Force -Restart'
            ]
            
            # Executa o comando
            self.status_updated.emit(_("domain.leaving"))
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.status_updated.emit(_("domain.leave_success"))
                self.finished.emit(True)
            else:
                error = result.stderr.strip()
                self.status_updated.emit(_("domain.leave_error").format(error=error))
                self.finished.emit(False)
                
        except Exception as e:
            logger.error(f"Erro ao remover do domínio: {e}")
            self.status_updated.emit(_("domain.leave_error").format(error=str(e)))
            self.finished.emit(False)
    
    def _update_domain(self):
        """Atualiza informações do domínio"""
        try:
            # Verifica se está em um domínio
            if not self._is_domain_member():
                self.status_updated.emit(_("domain.not_member"))
                self.finished.emit(False)
                return
            
            # Comando para atualizar relação com o domínio
            cmd = [
                'powershell',
                '-Command',
                'Test-ComputerSecureChannel -Repair'
            ]
            
            # Executa o comando
            self.status_updated.emit(_("domain.updating"))
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.status_updated.emit(_("domain.update_success"))
                self.finished.emit(True)
            else:
                error = result.stderr.strip()
                self.status_updated.emit(_("domain.update_error").format(error=error))
                self.finished.emit(False)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar domínio: {e}")
            self.status_updated.emit(_("domain.update_error").format(error=str(e)))
            self.finished.emit(False)
    
    def _is_domain_member(self):
        """Verifica se o computador está em um domínio"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            )
            
            domain = winreg.QueryValueEx(key, "Domain")[0]
            winreg.CloseKey(key)
            
            return bool(domain)
            
        except:
            return False

class DomainTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_domain_info()
        
    def setup_ui(self):
        # Remove o layout antigo se existir
        if self.layout():
            QWidget().setLayout(self.layout())
            
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Grupo de status
        status_group = QGroupBox()
        self.set_title_key(status_group, "domain.status_group")
        status_layout = QVBoxLayout()
        
        self.computer_name = QLabel()
        self.domain_status = QLabel()
        self.current_domain = QLabel()
        
        status_layout.addWidget(self.computer_name)
        status_layout.addWidget(self.domain_status)
        status_layout.addWidget(self.current_domain)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Grupo de ações
        actions_group = QGroupBox()
        self.set_title_key(actions_group, "domain.actions_group")
        actions_layout = QFormLayout()
        
        self.domain_input = QLineEdit()
        self.set_placeholder_key(self.domain_input, "domain.domain_name")
        
        self.username_input = QLineEdit()
        self.set_placeholder_key(self.username_input, "domain.username")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.set_placeholder_key(self.password_input, "domain.password")
        
        self.join_button = QPushButton()
        self.set_translation_key(self.join_button, "domain.join")
        self.join_button.clicked.connect(self.join_domain)
        
        self.leave_button = QPushButton()
        self.set_translation_key(self.leave_button, "domain.leave")
        self.leave_button.clicked.connect(self.leave_domain)
        
        self.update_button = QPushButton()
        self.set_translation_key(self.update_button, "domain.update")
        self.update_button.clicked.connect(self.update_domain)
        
        actions_layout.addRow(_("domain.domain_name"), self.domain_input)
        actions_layout.addRow(_("domain.username"), self.username_input)
        actions_layout.addRow(_("domain.password"), self.password_input)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.join_button)
        buttons_layout.addWidget(self.leave_button)
        buttons_layout.addWidget(self.update_button)
        
        actions_layout.addRow(buttons_layout)
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)
        
        self.setLayout(main_layout)
        self.update_translations()
        
    def load_domain_info(self):
        """Carrega informações do domínio"""
        try:
            # Obtém o nome do computador
            computer_name = socket.gethostname()
            # Obtém o nome do usuário atual
            username = getpass.getuser()
            
            # Atualiza as labels com as informações
            self.computer_name.setText(_("domain.computer_name").format(name=f"{computer_name} ({username})"))
            
            if self._is_domain_member():
                domain = self._get_domain_name()
                self.domain_status.setText(_("domain.current_domain").format(domain=domain))
                self.join_button.setEnabled(False)
                self.leave_button.setEnabled(True)
                self.update_button.setEnabled(True)
            else:
                self.domain_status.setText(_("domain.not_member"))
                self.join_button.setEnabled(True)
                self.leave_button.setEnabled(False)
                self.update_button.setEnabled(False)
                
        except Exception as e:
            logger.error(f"Erro ao carregar informações do domínio: {e}")
            self.domain_status.setText(_("domain.status_error"))
            
    def _is_domain_member(self):
        """Verifica se o computador está em um domínio"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            )
            
            domain = winreg.QueryValueEx(key, "Domain")[0]
            winreg.CloseKey(key)
            
            return bool(domain)
            
        except:
            return False
            
    def _get_domain_name(self):
        """Obtém o nome do domínio atual"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            )
            
            domain = winreg.QueryValueEx(key, "Domain")[0]
            winreg.CloseKey(key)
            
            return domain
            
        except:
            return _("domain.unknown")
            
    def join_domain(self):
        """Inicia processo de adicionar ao domínio"""
        try:
            domain = self.domain_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text()
            
            if not all([domain, username, password]):
                QMessageBox.warning(
                    self,
                    _("status.warning"),
                    _("domain.fill_all_fields")
                )
                return
            
            # Inicia worker
            self.worker = DomainWorker(
                "join",
                domain=domain,
                username=username,
                password=password
            )
            self.worker.status_updated.connect(self.update_status)
            self.worker.finished.connect(self.operation_finished)
            self.worker.start()
            
            # Desabilita interface
            self.join_button.setEnabled(False)
            self.domain_input.setEnabled(False)
            self.username_input.setEnabled(False)
            self.password_input.setEnabled(False)
            
        except Exception as e:
            logger.error(f"Erro ao iniciar processo de adicionar ao domínio: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("domain.join_error").format(error=str(e))
            )
            
    def leave_domain(self):
        """Inicia processo de remover do domínio"""
        try:
            reply = QMessageBox.question(
                self,
                _("domain.confirm_leave_title"),
                _("domain.confirm_leave"),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Inicia worker
                self.worker = DomainWorker("leave")
                self.worker.status_updated.connect(self.update_status)
                self.worker.finished.connect(self.operation_finished)
                self.worker.start()
                
                # Desabilita interface
                self.leave_button.setEnabled(False)
                self.update_button.setEnabled(False)
                
        except Exception as e:
            logger.error(f"Erro ao iniciar processo de remover do domínio: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("domain.leave_error").format(error=str(e))
            )
            
    def update_domain(self):
        """Inicia processo de atualizar relação com o domínio"""
        try:
            # Inicia worker
            self.worker = DomainWorker("update")
            self.worker.status_updated.connect(self.update_status)
            self.worker.finished.connect(self.operation_finished)
            self.worker.start()
            
            # Desabilita interface
            self.update_button.setEnabled(False)
            
        except Exception as e:
            logger.error(f"Erro ao iniciar processo de atualizar domínio: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("domain.update_error").format(error=str(e))
            )
            
    def update_status(self, message):
        """Atualiza mensagem de status"""
        self.domain_status.setText(message)
        
    def operation_finished(self, success):
        """Chamado quando uma operação é concluída"""
        # Recarrega informações
        self.load_domain_info()
        
        # Reabilita interface
        self.domain_input.setEnabled(True)
        self.username_input.setEnabled(True)
        self.password_input.setEnabled(True)
        
        if not success:
            QMessageBox.warning(
                self,
                _("status.error"),
                _("domain.operation_error").format(error=str(e))
            )
            
    def closeEvent(self, event):
        """Garante que o worker seja finalizado"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            
        event.accept() 