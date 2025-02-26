from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QSpacerItem, QSizePolicy, QGroupBox)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QFont, QDesktopServices
import os
from ...utils.logger import get_logger
from .base_tab import BaseTab
from ...utils.i18n import _
from ...version import get_version
import logging

logger = logging.getLogger(__name__)

class AboutTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Remove o layout antigo se existir
        if self.layout():
            QWidget().setLayout(self.layout())
            
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        self.logo_label = QLabel()
        logo_path = os.path.join("assets", "images", "logo.svg")
        try:
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_label.setPixmap(scaled_pixmap)
                self.logo_label.setAlignment(Qt.AlignCenter)
            else:
                raise Exception("Failed to load logo image")
        except Exception as e:
            logger.error(_("about.error_loading_logo").format(error=str(e)))
            self.logo_label.setText(_("about.title"))
            
        main_layout.addWidget(self.logo_label)
        
        # Título
        self.title_label = QLabel()
        self.set_translation_key(self.title_label, "about.title")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        main_layout.addWidget(self.title_label)
        
        # Versão
        self.version_label = QLabel()
        self.version_label.setText(_("about.version").format(version=get_version()))
        self.version_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.version_label)
        
        # Descrição
        self.description_label = QLabel()
        self.set_translation_key(self.description_label, "about.description")
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setWordWrap(True)
        main_layout.addWidget(self.description_label)
        
        # Contato
        contact_group = QGroupBox()
        self.set_title_key(contact_group, "about.contact")
        contact_layout = QVBoxLayout()
        
        self.email_label = QLabel()
        self.set_translation_key(self.email_label, "about.email")
        self.email_label.setAlignment(Qt.AlignCenter)
        contact_layout.addWidget(self.email_label)
        
        self.phone_label = QLabel()
        self.set_translation_key(self.phone_label, "about.phone")
        self.phone_label.setAlignment(Qt.AlignCenter)
        contact_layout.addWidget(self.phone_label)
        
        contact_group.setLayout(contact_layout)
        main_layout.addWidget(contact_group)
        
        # Botão de website
        self.website_button = QPushButton()
        self.set_translation_key(self.website_button, "about.visit_website")
        self.website_button.clicked.connect(self.open_website)
        main_layout.addWidget(self.website_button)
        
        # Copyright
        self.copyright_label = QLabel()
        self.set_translation_key(self.copyright_label, "about.copyright")
        self.copyright_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.copyright_label)
        
        self.setLayout(main_layout)
        self.update_translations()

    def open_website(self):
        QDesktopServices.openUrl(QUrl("https://www.adfinfoservices.com.br"))

    def update_translations(self):
        """Atualiza as traduções da interface"""
        super().update_translations()
        self.version_label.setText(_("about.version").format(version=get_version()))
        
        contact_text = f"{_('about.contact')}\n{_('about.email')}\n{_('about.phone')}"
        self.email_label.setText(contact_text)
        
        self.website_button.setText(_("about.visit_website")) 