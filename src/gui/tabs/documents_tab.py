"""
Aba de documentos do ADF System Manager.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QHBoxLayout, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
import os
from src.utils.logger import Logger
from src.utils.i18n import _
from src.gui.viewers import DocumentViewer

class DocumentsTab(QWidget):
    """Aba para gerenciamento de documentos."""
    
    def __init__(self, parent=None):
        """Inicializa a aba de documentos."""
        super().__init__(parent)
        self.logger = Logger(__name__)
        self.document_viewer = None
        self.setup_ui()
        self.load_documents()
        
    def setup_ui(self):
        """Configura a interface da aba."""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel(_("documents.title"))
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Lista de documentos
        self.documents_list = QListWidget()
        self.documents_list.itemDoubleClicked.connect(self.open_document)
        layout.addWidget(self.documents_list)
        
        # Botões
        button_layout = QHBoxLayout()
        
        view_button = QPushButton(_("documents.view"))
        view_button.clicked.connect(self.view_selected_document)
        button_layout.addWidget(view_button)
        
        refresh_button = QPushButton(_("documents.refresh"))
        refresh_button.clicked.connect(self.load_documents)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
    def load_documents(self):
        """Carrega a lista de documentos disponíveis."""
        try:
            self.documents_list.clear()
            
            # Lista de extensões suportadas
            supported_extensions = ['.rtf', '.txt', '.md', '.doc', '.docx']
            
            # Verifica e adiciona o manual principal (adf.rtf)
            manual_path = os.path.join("assets", "docs", "adf.rtf")
            if os.path.exists(manual_path):
                self.documents_list.addItem("Manual e Termos de Uso")
            
            # Verifica outros documentos no diretório
            docs_path = os.path.join("assets", "docs")
            if os.path.exists(docs_path):
                for file in os.listdir(docs_path):
                    if file.lower() != "adf.rtf" and any(file.lower().endswith(ext) for ext in supported_extensions):
                        self.documents_list.addItem(file)
            
            self.logger.info("Lista de documentos atualizada")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar documentos: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("documents.error_loading")
            )
            
    def get_document_path(self, item_text):
        """Retorna o caminho completo do documento."""
        if item_text == "Manual e Termos de Uso":
            return os.path.join("assets", "docs", "adf.rtf")
        return os.path.join("assets", "docs", item_text)
        
    def view_selected_document(self):
        """Abre o documento selecionado no visualizador."""
        current_item = self.documents_list.currentItem()
        if current_item:
            self.open_document(current_item)
        else:
            QMessageBox.information(
                self,
                _("status.warning"),
                _("documents.select_document")
            )
            
    def open_document(self, item):
        """Abre um documento no visualizador."""
        try:
            doc_path = self.get_document_path(item.text())
            
            if not os.path.exists(doc_path):
                raise FileNotFoundError(_("documents.document_not_found").format(doc_path))
                
            # Cria uma nova instância do visualizador se não existir
            if not self.document_viewer:
                self.document_viewer = DocumentViewer(self)
            
            # Carrega e exibe o documento
            self.document_viewer.load_document(doc_path)
            self.document_viewer.show()
            self.document_viewer.raise_()
            self.document_viewer.activateWindow()
            
            self.logger.info(f"Documento aberto: {doc_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao abrir documento: {e}")
            QMessageBox.warning(
                self,
                _("status.error"),
                _("documents.error_opening").format(str(e))
            ) 