class StyleSheet:
    # Estilo geral da aplicação
    APP = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        QMenuBar {
            background-color: #2c3e50;
            color: white;
            padding: 5px;
        }
        
        QMenuBar::item {
            padding: 5px 10px;
            background-color: transparent;
        }
        
        QMenuBar::item:selected {
            background-color: #34495e;
        }
        
        QMenu {
            background-color: #2c3e50;
            color: white;
            border: 1px solid #34495e;
        }
        
        QMenu::item:selected {
            background-color: #34495e;
        }
        
        QStatusBar {
            background-color: #2c3e50;
            color: white;
            padding: 5px;
        }
        
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QPushButton:pressed {
            background-color: #2472a4;
        }
        
        QProgressBar {
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #3498db;
            width: 10px;
        }
    """
    
    # Estilo específico para a aba Sistema
    SYSTEM_TAB = """
        QLabel[class="section-title"] {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px 0;
        }
        
        QLabel {
            color: #2c3e50;
            padding: 5px;
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        }
        
        QScrollArea {
            border: none;
        }
        
        QWidget#container {
            background-color: #f9f9f9;
        }
    """
    
    # Estilo para a aba de Monitoramento
    MONITORING_TAB = """
        QLabel[class="metric-title"] {
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        QLabel[class="metric-value"] {
            font-size: 24px;
            color: #3498db;
        }
        
        QLabel[class="metric-unit"] {
            font-size: 12px;
            color: #7f8c8d;
        }
        
        QFrame[class="metric-card"] {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
        }
    """
    
    # Estilo para a aba de Backup
    BACKUP_TAB = """
        QLabel[class="backup-title"] {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px 0;
        }
        
        QPushButton[class="backup-button"] {
            background-color: #27ae60;
            padding: 10px 20px;
            font-size: 14px;
        }
        
        QPushButton[class="backup-button"]:hover {
            background-color: #219a52;
        }
        
        QProgressBar {
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #27ae60;
        }
    """
    
    # Estilo para a aba de Ferramentas
    TOOLS_TAB = """
        QPushButton[class="tool-button"] {
            background-color: #9b59b6;
            padding: 15px;
            font-size: 14px;
            text-align: left;
        }
        
        QPushButton[class="tool-button"]:hover {
            background-color: #8e44ad;
        }
        
        QLabel[class="tool-description"] {
            color: #7f8c8d;
            font-size: 12px;
        }
    """
    
    # Estilo para diálogos
    DIALOG = """
        QDialog {
            background-color: #f0f0f0;
        }
        
        QLabel {
            color: #2c3e50;
        }
        
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
    """
    
    # Estilo para mensagens de erro
    ERROR = """
        QLabel {
            color: #c0392b;
            font-weight: bold;
        }
        
        QPushButton {
            background-color: #e74c3c;
        }
        
        QPushButton:hover {
            background-color: #c0392b;
        }
    """
    
    # Estilo para mensagens de sucesso
    SUCCESS = """
        QLabel {
            color: #27ae60;
            font-weight: bold;
        }
        
        QPushButton {
            background-color: #2ecc71;
        }
        
        QPushButton:hover {
            background-color: #27ae60;
        }
    """ 