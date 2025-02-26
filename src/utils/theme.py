from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def apply_theme(widget, theme_name):
    """Aplica o tema especificado ao widget"""
    if theme_name == "dark":
        # Tema escuro
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # Aplica a paleta ao widget e seus filhos
        widget.setPalette(palette)
        QApplication.instance().setPalette(palette)
        
    else:
        # Tema claro (padrão)
        QApplication.instance().setPalette(QApplication.style().standardPalette())
        widget.setPalette(QApplication.style().standardPalette()) 