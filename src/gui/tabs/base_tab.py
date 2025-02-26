from PyQt5.QtWidgets import QWidget
from ...utils.i18n import _

class BaseTab(QWidget):
    def __init__(self):
        super().__init__()
    
    def setup_ui(self):
        """Método a ser implementado pelas classes filhas"""
        pass
    
    def update_translations(self):
        """Atualiza as traduções dos elementos da interface"""
        # Atualiza labels
        for child in self.findChildren(QWidget):
            if hasattr(child, 'translation_key'):
                child.setText(_(child.translation_key))
            elif hasattr(child, 'title_key'):
                child.setTitle(_(child.title_key))
            elif hasattr(child, 'placeholder_key'):
                child.setPlaceholderText(_(child.placeholder_key))
    
    def set_translation_key(self, widget, key):
        """Define a chave de tradução para um widget"""
        widget.translation_key = key
        widget.setText(_(key))
    
    def set_title_key(self, widget, key):
        """Define a chave de tradução para o título de um widget"""
        widget.title_key = key
        widget.setTitle(_(key))
    
    def set_placeholder_key(self, widget, key):
        """Define a chave de tradução para o placeholder de um widget"""
        widget.placeholder_key = key
        widget.setPlaceholderText(_(key)) 