from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTabWidget, QLabel, QPushButton, QStatusBar,
                            QMessageBox, QProgressBar, QProgressDialog, QFileDialog,
                            QMenu, QAction, QActionGroup, QMenuBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon
from .tabs.system_tab import SystemTab
from .tabs.domain_tab import DomainTab
from .tabs.software_tab import SoftwareTab
from .tabs.updates_tab import UpdatesTab
from .tabs.about_tab import AboutTab
from .tabs.monitoring_tab import MonitoringTab
from .tabs.backup_tab import BackupTab
from .tabs.tools_tab import ToolsTab
from .tabs.settings_tab import SettingsTab
from .tabs.documents_tab import DocumentsTab
from ..utils.themes import set_theme, ThemeManager
from ..utils.updater import UpdateWorker
from ..utils.logger import get_logger
from ..utils.report import export_report
from ..utils.i18n import get_i18n, _
from ..utils.config import get_config_value, update_config
from ..utils.theme import apply_theme
from ..version import get_version
import os
import sys

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.i18n = get_i18n()
        self.setWindowTitle(f"{_('app_name')} - {get_version()}")
        
        # Define o ícone da aplicação
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'assets', 'icons', 'app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Configuração da janela
        self.setMinimumSize(800, 600)
        
        # Cria a barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(_("status.ready"))
        
        # Configura a interface
        self.setup_ui()
        
        # Cria os menus
        self.create_menu()
        
        # Aplica o tema
        set_theme(self.config.get('theme', 'light'))
        
        # Inicia verificação de atualizações
        if self.config.get('update_check', True):
            self.check_for_updates()
        
    def setup_ui(self):
        """Configura a interface da janela principal."""
        # Cria o widget de abas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Adiciona as abas
        self.system_tab = SystemTab()
        self.tools_tab = ToolsTab()
        self.updates_tab = UpdatesTab()
        self.software_tab = SoftwareTab()
        self.domain_tab = DomainTab()
        self.backup_tab = BackupTab()
        self.about_tab = AboutTab()
        self.monitoring_tab = MonitoringTab()
        self.settings_tab = SettingsTab()
        self.documents_tab = DocumentsTab()
        
        # Mapeia o nome da classe para a chave de tradução
        self.tab_translations = {
            'SystemTab': 'system',
            'ToolsTab': 'tools',
            'UpdatesTab': 'updates',
            'SoftwareTab': 'software',
            'DomainTab': 'domain',
            'BackupTab': 'backup',
            'AboutTab': 'about',
            'MonitoringTab': 'monitoring',
            'SettingsTab': 'settings',
            'DocumentsTab': 'documents'
        }
        
        # Adiciona as abas com suas traduções
        self.tabs.addTab(self.system_tab, _("tabs.system"))
        self.tabs.addTab(self.tools_tab, _("tabs.tools"))
        self.tabs.addTab(self.updates_tab, _("tabs.updates"))
        self.tabs.addTab(self.software_tab, _("tabs.software"))
        self.tabs.addTab(self.domain_tab, _("tabs.domain"))
        self.tabs.addTab(self.backup_tab, _("tabs.backup"))
        self.tabs.addTab(self.monitoring_tab, _("tabs.monitoring"))
        self.tabs.addTab(self.about_tab, _("tabs.about"))
        self.tabs.addTab(self.settings_tab, _("tabs.settings"))
        self.tabs.addTab(self.documents_tab, _("tabs.documents"))
        
        # Aplica o tema
        ThemeManager.apply_theme(self)
        
        # Define o tamanho e posição inicial
        self.resize(800, 600)
        self.center_window()
        
    def create_menu(self):
        menubar = QMenuBar()
        self.setMenuBar(menubar)
        
        # Menu Arquivo
        file_menu = QMenu(_("menu.file"), self)
        menubar.addMenu(file_menu)
        
        export_action = file_menu.addAction(_("menu.export_report"))
        export_action.triggered.connect(self.export_report)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction(_("menu.exit"))
        exit_action.triggered.connect(self.close)
        
        # Menu Ferramentas
        tools_menu = QMenu(_("menu.tools"), self)
        menubar.addMenu(tools_menu)
        
        clean_action = tools_menu.addAction(_("tools.clean_temp"))
        clean_action.triggered.connect(self.tools_tab.clean_temp_files)
        
        optimize_action = tools_menu.addAction(_("tools.optimize"))
        optimize_action.triggered.connect(self.tools_tab.optimize_system)
        
        # Menu Configurações
        settings_menu = QMenu(_("menu.settings"), self)
        menubar.addMenu(settings_menu)
        
        # Submenu de Idiomas
        language_menu = QMenu(_("settings.language"), self)
        settings_menu.addMenu(language_menu)
        language_group = QActionGroup(self)
        
        # Adiciona ações para cada idioma disponível
        for lang in self.i18n.get_available_languages():
            action = QAction(lang, self, checkable=True)
            action.setChecked(lang == self.i18n.current_language)
            action.triggered.connect(lambda checked, l=lang: self.change_language(l))
            language_group.addAction(action)
            language_menu.addAction(action)
        
        # Submenu de Temas
        theme_menu = QMenu(_("settings.theme"), self)
        settings_menu.addMenu(theme_menu)
        light_action = theme_menu.addAction(_("settings.light"))
        dark_action = theme_menu.addAction(_("settings.dark"))
        
        light_action.triggered.connect(lambda: self.change_theme('light'))
        dark_action.triggered.connect(lambda: self.change_theme('dark'))
        
        # Menu Ajuda
        help_menu = QMenu(_("menu.help"), self)
        menubar.addMenu(help_menu)
        
        about_action = help_menu.addAction(_("tabs.about"))
        about_action.triggered.connect(self.show_about)
        
        update_action = help_menu.addAction(_("tabs.updates"))
        update_action.triggered.connect(self.check_for_updates)
        
    def change_language(self, language: str):
        """Altera o idioma da aplicação"""
        if self.i18n.set_language(language):
            # Atualiza a interface
            self.setWindowTitle(f"{_('app_name')} - {get_version()}")
            self.status_bar.showMessage(_("status.ready"))
            
            # Recria os menus com o novo idioma
            self.menuBar().clear()
            self.create_menu()
            
            # Atualiza as abas
            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                class_name = tab.__class__.__name__
                if class_name in self.tab_translations:
                    key = f"tabs.{self.tab_translations[class_name]}"
                    self.tabs.setTabText(i, _(key))
            
            # Atualiza o conteúdo das abas
            for tab in [self.system_tab, self.tools_tab, self.updates_tab, 
                       self.software_tab, self.domain_tab, self.backup_tab, 
                       self.about_tab, self.monitoring_tab, self.settings_tab, 
                       self.documents_tab]:
                if hasattr(tab, 'update_translations'):
                    tab.update_translations()
        
    def change_theme(self, theme: str):
        """Altera o tema da aplicação"""
        set_theme(theme)
        self.config['theme'] = theme
        
    def check_for_updates(self):
        """Verifica se há atualizações disponíveis"""
        self.status_bar.showMessage(_("status.processing"))
        self.update_worker = UpdateWorker()
        self.update_worker.finished.connect(self.handle_update_result)
        self.update_worker.error.connect(self.handle_update_error)
        self.update_worker.start()
        
    def handle_update_result(self, result):
        """Trata o resultado da verificação de atualizações"""
        if result['available']:
            message = _("Uma nova versão ({0}) está disponível.").format(result['version'])
            if result['required']:
                message += "\n" + _("Esta é uma atualização obrigatória.")
                
            # Exibe as notas de atualização
            if 'notes' in result:
                message += "\n\n" + _("Notas da versão:") + "\n"
                for note in result['notes']:
                    message += f"• {note}\n"
                    
            # Pergunta se deseja atualizar
            reply = QMessageBox.question(
                self,
                _("Atualização Disponível"),
                message + "\n\n" + _("Deseja atualizar agora?"),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.download_update(result['url'], result['version'])
        else:
            # Apenas atualiza a barra de status quando não há atualizações
            self.status_bar.showMessage(_("Você está usando a versão mais recente"))
        
    def handle_update_error(self, error):
        """Trata erros na verificação de atualizações"""
        self.status_bar.showMessage(_("Erro ao verificar atualizações"))
        QMessageBox.warning(
            self,
            _("Erro na Verificação"),
            _("Não foi possível verificar atualizações:\n{0}").format(error)
        )
        
    def download_update(self, url, version):
        """Baixa e instala a atualização"""
        try:
            self.status_bar.showMessage(_("Baixando atualização..."))
            
            # Cria e inicia o worker de download
            self.download_worker = UpdateWorker()
            self.download_worker.finished.connect(lambda: self.handle_download_result(version))
            self.download_worker.error.connect(self.handle_download_error)
            self.download_worker.start()
            
        except Exception as e:
            self.status_bar.showMessage(_("Erro ao baixar atualização"))
            QMessageBox.critical(
                self,
                _("Erro"),
                _("Erro ao baixar atualização: {0}").format(str(e))
            )
            
    def handle_download_result(self, version):
        """Trata o resultado do download da atualização"""
        self.status_bar.showMessage(_("Download concluído"))
        
        # Exibe mensagem de sucesso
        QMessageBox.information(
            self,
            _("Atualização Concluída"),
            _("A atualização foi baixada com sucesso. A aplicação será reiniciada para aplicar as alterações.")
        )
        
        # Reinicia a aplicação
        python = sys.executable
        os.execl(python, python, *sys.argv)
        
    def handle_download_error(self, error):
        """Trata erros no download da atualização"""
        self.status_bar.showMessage(_("Erro ao baixar atualização"))
        QMessageBox.critical(
            self,
            _("Erro"),
            _("Erro ao baixar atualização: {0}").format(error)
        )
        
    def export_report(self):
        """Exporta relatório do sistema"""
        try:
            # Solicita local para salvar o arquivo
            filename, _ = QFileDialog.getSaveFileName(
                self,
                _("report.title"),
                os.path.join(os.path.expanduser('~'), 'Desktop', 'relatorio_sistema.html'),
                "Arquivo HTML (*.html)"
            )
            
            if filename:
                # Exporta o relatório
                success, result = export_report(filename)
                
                if success:
                    self.status_bar.showMessage(_("report.export_success"))
                    QMessageBox.information(
                        self,
                        _("status.completed"),
                        f"{_('report.export_success')}\n{_('report.generated')}: {result}"
                    )
                else:
                    self.status_bar.showMessage(_("report.export_error"))
                    QMessageBox.warning(
                        self,
                        _("status.error"),
                        f"{_('report.export_error')}:\n{result}"
                    )
            else:
                self.status_bar.showMessage(_("status.ready"))
            
        except Exception as e:
            logger.error(f"Erro ao exportar relatório: {e}")
            self.status_bar.showMessage(_("report.export_error"))
            QMessageBox.warning(
                self,
                _("status.error"),
                f"{_('report.export_error')}:\n{e}"
            )
        
    def show_about(self):
        QMessageBox.about(self, _("tabs.about"), 
            f"{_('app_name')}\n"
            "Versão: 1.0.0\n"
            "© 2024 ADF Serviços de Informática\n"
            "Todos os direitos reservados")

    def closeEvent(self, event):
        """Confirma o fechamento da aplicação"""
        reply = QMessageBox.question(
            self,
            _("app_name"),
            _("messages.confirm_exit"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center_window(self):
        """Centraliza a janela na tela."""
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft()) 