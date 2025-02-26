"""
Aba de configurações do ADF System Manager.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox,
    QComboBox, QLabel, QSpinBox, QHBoxLayout,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from src.utils.logger import Logger
from src.utils.i18n import _
from src.utils.themes import ThemeManager
from src.utils.config import get_config_value, update_config

class SettingsTab(QWidget):
    """Aba para configurações do sistema."""
    
    def __init__(self, parent=None):
        """Inicializa a aba de configurações."""
        super().__init__(parent)
        self.logger = Logger(__name__)
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Configura a interface da aba."""
        layout = QVBoxLayout(self)
        
        # Grupo de Aparência
        appearance_group = QGroupBox(_("settings.appearance"))
        appearance_layout = QVBoxLayout()
        
        # Tema
        theme_layout = QHBoxLayout()
        theme_label = QLabel(_("settings.theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([_("settings.light"), _("settings.dark")])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        appearance_layout.addLayout(theme_layout)
        
        # Idioma
        language_layout = QHBoxLayout()
        language_label = QLabel(_("settings.language"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Português (BR)", "English (US)"])
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        appearance_layout.addLayout(language_layout)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Grupo de Atualizações
        updates_group = QGroupBox(_("settings.updates"))
        updates_layout = QVBoxLayout()
        
        self.check_updates = QCheckBox(_("settings.check_updates"))
        updates_layout.addWidget(self.check_updates)
        
        self.auto_update = QCheckBox(_("settings.auto_update"))
        updates_layout.addWidget(self.auto_update)
        
        updates_group.setLayout(updates_layout)
        layout.addWidget(updates_group)
        
        # Grupo de Monitoramento
        monitoring_group = QGroupBox(_("settings.monitoring"))
        monitoring_layout = QVBoxLayout()
        
        self.enable_monitoring = QCheckBox(_("settings.enable_monitoring"))
        monitoring_layout.addWidget(self.enable_monitoring)
        
        interval_layout = QHBoxLayout()
        interval_label = QLabel(_("settings.update_interval"))
        self.update_interval = QSpinBox()
        self.update_interval.setRange(1, 60)
        self.update_interval.setSuffix(_("settings.seconds"))
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.update_interval)
        monitoring_layout.addLayout(interval_layout)
        
        monitoring_group.setLayout(monitoring_layout)
        layout.addWidget(monitoring_group)
        
        # Botões
        button_layout = QHBoxLayout()
        
        save_button = QPushButton(_("settings.save"))
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        reset_button = QPushButton(_("settings.reset"))
        reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
    def load_settings(self):
        """Carrega as configurações salvas."""
        try:
            # Tema
            theme = get_config_value('theme', 'light')
            self.theme_combo.setCurrentText(
                _("settings.light") if theme == 'light' else _("settings.dark")
            )
            
            # Idioma
            language = get_config_value('language', 'pt_BR')
            self.language_combo.setCurrentText(
                "Português (BR)" if language == 'pt_BR' else "English (US)"
            )
            
            # Atualizações
            self.check_updates.setChecked(get_config_value('check_updates', True))
            self.auto_update.setChecked(get_config_value('auto_update', False))
            
            # Monitoramento
            self.enable_monitoring.setChecked(get_config_value('enable_monitoring', True))
            self.update_interval.setValue(get_config_value('update_interval', 5))
            
            self.logger.info("Configurações carregadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("settings.load_error")
            )
            
    def save_settings(self):
        """Salva as configurações."""
        try:
            # Tema
            theme = 'light' if self.theme_combo.currentText() == _("settings.light") else 'dark'
            update_config('theme', theme)
            ThemeManager.apply_theme(self.window())
            
            # Idioma
            language = 'pt_BR' if self.language_combo.currentText() == "Português (BR)" else 'en_US'
            update_config('language', language)
            
            # Atualizações
            update_config('check_updates', self.check_updates.isChecked())
            update_config('auto_update', self.auto_update.isChecked())
            
            # Monitoramento
            update_config('enable_monitoring', self.enable_monitoring.isChecked())
            update_config('update_interval', self.update_interval.value())
            
            self.logger.info("Configurações salvas com sucesso")
            QMessageBox.information(
                self,
                _("status.completed"),
                _("settings.save_success")
            )
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("settings.save_error")
            )
            
    def reset_settings(self):
        """Restaura as configurações padrão."""
        try:
            # Configurações padrão
            default_settings = {
                'theme': 'light',
                'language': 'pt_BR',
                'check_updates': True,
                'auto_update': False,
                'enable_monitoring': True,
                'update_interval': 5
            }
            
            # Atualiza a interface
            self.theme_combo.setCurrentText(_("settings.light"))
            self.language_combo.setCurrentText("Português (BR)")
            self.check_updates.setChecked(True)
            self.auto_update.setChecked(False)
            self.enable_monitoring.setChecked(True)
            self.update_interval.setValue(5)
            
            # Salva as configurações
            for key, value in default_settings.items():
                update_config(key, value)
            
            # Aplica o tema
            ThemeManager.apply_theme(self.window())
            
            self.logger.info("Configurações restauradas para o padrão")
            QMessageBox.information(
                self,
                _("status.completed"),
                _("settings.reset_success")
            )
        except Exception as e:
            self.logger.error(f"Erro ao restaurar configurações: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("settings.reset_error")
            ) 