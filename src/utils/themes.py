"""
Módulo de gerenciamento de temas do ADF System Manager.
"""

import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QLabel,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox,
    QRadioButton, QGroupBox, QProgressBar, QTableWidget,
    QListWidget
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from .logger import get_logger

logger = get_logger(__name__)

class ThemeManager:
    """Gerenciador de temas da aplicação."""
    
    @staticmethod
    def apply_theme(widget, theme='light'):
        """Aplica um tema ao widget e seus filhos."""
        if theme == 'dark':
            ThemeManager._apply_dark_theme(widget)
        else:
            ThemeManager._apply_light_theme(widget)
            
    @staticmethod
    def _apply_light_theme(widget):
        """Aplica o tema claro."""
        palette = QPalette()
        
        # Cores do tema claro
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 120, 212))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 212))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # Aplica a paleta ao widget principal
        widget.setPalette(palette)
        if not isinstance(widget, QApplication):
            widget.setAutoFillBackground(True)
        
        # Aplica o tema aos widgets filhos
        for child in widget.findChildren(QWidget):
            child.setPalette(palette)
            child.setAutoFillBackground(True)
            
            # Aplica estilos específicos para cada tipo de widget
            if isinstance(child, QPushButton):
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        color: #000000;
                        border: 1px solid #d0d0d0;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                    }
                """)
            elif isinstance(child, QLineEdit) or isinstance(child, QTextEdit):
                child.setStyleSheet("""
                    QLineEdit, QTextEdit {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #d0d0d0;
                        padding: 3px;
                    }
                """)
            elif isinstance(child, QComboBox):
                child.setStyleSheet("""
                    QComboBox {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #d0d0d0;
                        padding: 3px;
                    }
                """)
            elif isinstance(child, QGroupBox):
                child.setStyleSheet("""
                    QGroupBox {
                        background-color: #f5f5f5;
                        border: 1px solid #d0d0d0;
                        margin-top: 5px;
                        padding-top: 10px;
                    }
                    QGroupBox::title {
                        color: #000000;
                    }
                """)
            elif isinstance(child, (QTableWidget, QListWidget)):
                child.setStyleSheet("""
                    QTableWidget, QListWidget {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #d0d0d0;
                    }
                    QHeaderView::section {
                        background-color: #f0f0f0;
                        color: #000000;
                        border: 1px solid #d0d0d0;
                    }
                """)
            
    @staticmethod
    def _apply_dark_theme(widget):
        """Aplica o tema escuro."""
        palette = QPalette()
        
        # Cores do tema escuro
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, QColor(35, 35, 35))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 120, 212))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 212))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # Aplica a paleta ao widget principal
        widget.setPalette(palette)
        if not isinstance(widget, QApplication):
            widget.setAutoFillBackground(True)
        
        # Aplica o tema aos widgets filhos
        for child in widget.findChildren(QWidget):
            child.setPalette(palette)
            child.setAutoFillBackground(True)
            
            # Aplica estilos específicos para cada tipo de widget
            if isinstance(child, QPushButton):
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #404040;
                        color: #ffffff;
                        border: 1px solid #505050;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                    }
                    QPushButton:pressed {
                        background-color: #606060;
                    }
                """)
            elif isinstance(child, QLineEdit) or isinstance(child, QTextEdit):
                child.setStyleSheet("""
                    QLineEdit, QTextEdit {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 1px solid #505050;
                        padding: 3px;
                    }
                """)
            elif isinstance(child, QComboBox):
                child.setStyleSheet("""
                    QComboBox {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 1px solid #505050;
                        padding: 3px;
                    }
                """)
            elif isinstance(child, QGroupBox):
                child.setStyleSheet("""
                    QGroupBox {
                        background-color: #353535;
                        border: 1px solid #505050;
                        margin-top: 5px;
                        padding-top: 10px;
                    }
                    QGroupBox::title {
                        color: #ffffff;
                    }
                """)
            elif isinstance(child, (QTableWidget, QListWidget)):
                child.setStyleSheet("""
                    QTableWidget, QListWidget {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 1px solid #505050;
                    }
                    QHeaderView::section {
                        background-color: #404040;
                        color: #ffffff;
                        border: 1px solid #505050;
                    }
                """)

def set_theme(theme='light'):
    """Define o tema global da aplicação."""
    app = QApplication.instance()
    if app:
        ThemeManager.apply_theme(app, theme)
        # Força a atualização de todos os widgets
        for widget in app.allWidgets():
            widget.update()

def load_theme_file():
    """Carrega o arquivo de temas"""
    try:
        theme_path = os.path.join(os.path.dirname(__file__), 'themes.json')
        with open(theme_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo de temas: {e}")
        return None

def get_theme_colors(theme_name='light'):
    """Retorna as cores do tema especificado"""
    themes = load_theme_file()
    if not themes or theme_name not in themes:
        logger.warning(f"Tema '{theme_name}' não encontrado, usando tema claro")
        return get_default_theme()
    return themes[theme_name]

def get_default_theme():
    """Retorna o tema padrão (claro)"""
    return {
        "window": {
            "background": "#ffffff",
            "text": "#000000"
        },
        "menu": {
            "background": "#f0f0f0",
            "text": "#000000",
            "hover": "#e0e0e0"
        },
        "tab": {
            "background": "#f5f5f5",
            "text": "#000000",
            "selected": "#ffffff",
            "border": "#d0d0d0"
        },
        "button": {
            "background": "#0078d4",
            "text": "#ffffff",
            "hover": "#006cbd",
            "disabled": "#cccccc"
        },
        "input": {
            "background": "#ffffff",
            "text": "#000000",
            "border": "#d0d0d0",
            "placeholder": "#757575"
        },
        "status": {
            "background": "#f0f0f0",
            "text": "#000000",
            "border": "#d0d0d0"
        }
    } 