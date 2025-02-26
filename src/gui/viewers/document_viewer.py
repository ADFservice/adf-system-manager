"""
Visualizador de documentos do ADF System Manager.
Suporta visualização de arquivos RTF e outros formatos usando Pandoc.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QPushButton, QVBoxLayout, 
    QWidget, QLabel, QMessageBox, QProgressDialog
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon
import json
import os
import pypandoc
from src.utils.logger import Logger
from src.utils.themes import ThemeManager
from src.utils.i18n import _

class DocumentViewer(QMainWindow):
    """Janela principal do visualizador de documentos."""
    
    def __init__(self, parent=None):
        """Inicializa o visualizador de documentos."""
        super().__init__(parent)
        self.logger = Logger(__name__)
        self.settings = QSettings('ADF', 'SystemManager')
        self.setup_ui()
        self.setup_pandoc()
        
    def setup_ui(self):
        """Configura a interface do usuário."""
        self.setWindowTitle(_("viewer.title"))
        self.setWindowIcon(QIcon(os.path.join("assets", "icons", "app_icon.ico")))
        
        # Widget central e layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Área de texto
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)
        
        # Botão de fechar
        close_button = QPushButton(_("viewer.close"))
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        # Aplicar tema
        ThemeManager.apply_theme(self)
        
        # Definir tamanho e posição
        self.resize(int(self.screen().size().width() * 0.7),
                   int(self.screen().size().height() * 0.7))
        self.center_window()
        
    def center_window(self):
        """Centraliza a janela na tela."""
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())
        
    def setup_pandoc(self):
        """Configura o Pandoc para conversão de documentos."""
        try:
            pypandoc.get_pandoc_version()
            self.logger.info("Pandoc encontrado no sistema")
        except OSError:
            self.logger.info("Pandoc não encontrado. Iniciando download...")
            progress = QProgressDialog(
                _("Instalando Pandoc..."),
                None, 0, 0, self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            try:
                pypandoc.download_pandoc()
                self.logger.info("Pandoc instalado com sucesso")
            except Exception as e:
                self.logger.error(f"Erro ao instalar Pandoc: {e}")
                QMessageBox.critical(
                    self,
                    _("viewer.error"),
                    _("viewer.pandoc_error")
                )
            finally:
                progress.close()
                
    def load_document(self, file_path):
        """Carrega e exibe um documento."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(_("viewer.file_not_found").format(file_path))
            
            # Mostra diálogo de progresso
            progress = QProgressDialog(
                _("Carregando documento..."),
                None, 0, 0, self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            try:
                # Converte o documento para texto
                text = pypandoc.convert_file(file_path, 'plain', encoding='utf-8')
                self.text_area.setPlainText(text)
                self.logger.info(f"Documento carregado com sucesso: {file_path}")
                
            finally:
                progress.close()
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar documento: {e}")
            self.text_area.setPlainText(_("viewer.error_loading").format(str(e)))
            QMessageBox.warning(
                self,
                _("viewer.error"),
                _("viewer.error_loading").format(str(e))
            )
            
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela."""
        self.logger.info("Fechando o visualizador de documentos")
        event.accept() 