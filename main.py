import sys
import os
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.utils.logger import get_logger, setup_logging
from src.utils.config import load_config

def main():
    # Configura o logging
    setup_logging()
    logger = get_logger(__name__)
    
    try:
        # Carrega a configuração
        config = load_config()
        
        # Cria a aplicação
        app = QApplication(sys.argv)
        
        # Cria a janela principal
        window = MainWindow(config)
        window.show()
        
        # Executa a aplicação
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Erro ao iniciar aplicação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 