"""
Módulo de logging do ADF System Manager.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from .constants import LOG_MAX_BYTES, LOG_BACKUP_COUNT
from logging.handlers import RotatingFileHandler

def get_log_path():
    """Retorna o caminho do arquivo de log"""
    if os.name == 'nt':  # Windows
        log_dir = os.path.join(os.getenv('APPDATA'), 'ADF', 'logs')
    else:  # Linux/Mac
        log_dir = os.path.join(os.path.expanduser('~'), '.config', 'adf', 'logs')
        
    # Cria o diretório se não existir
    os.makedirs(log_dir, exist_ok=True)
    
    return os.path.join(log_dir, 'adf-system-manager.log')

def setup_logging(debug=False):
    """Configura o sistema de logging"""
    # Define o nível de log
    level = logging.DEBUG if debug else logging.INFO
    
    # Configura o formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configura o handler de arquivo
    file_handler = logging.handlers.RotatingFileHandler(
        get_log_path(),
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Configura o handler de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configura o logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove handlers existentes
    root_logger.handlers = []
    
    # Adiciona os handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log inicial
    root_logger.info("Sistema de logging iniciado")
    if debug:
        root_logger.debug("Modo debug ativado")

def get_logger(name):
    """Retorna uma instância do logger."""
    return Logger(name)

class Logger:
    """Classe para gerenciamento de logs."""
    
    def __init__(self, name):
        """Inicializa o logger."""
        self.logger = logging.getLogger(name)
        
        if not self.logger.handlers:
            self.setup_logger()
            
    def setup_logger(self):
        """Configura o logger."""
        self.logger.setLevel(logging.DEBUG)
        
        # Cria o diretório de logs se não existir
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Nome do arquivo de log com data
        log_file = os.path.join(
            log_dir,
            f"adf_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # Handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adiciona os handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def debug(self, message):
        """Registra mensagem de debug."""
        self.logger.debug(message)
        
    def info(self, message):
        """Registra mensagem informativa."""
        self.logger.info(message)
        
    def warning(self, message):
        """Registra mensagem de aviso."""
        self.logger.warning(message)
        
    def error(self, message):
        """Registra mensagem de erro."""
        self.logger.error(message)
        
    def critical(self, message):
        """Registra mensagem crítica."""
        self.logger.critical(message)
        
class LogManager:
    """Gerenciador de logs com funcionalidades adicionais"""
    
    @staticmethod
    def log_system_info(system_info):
        """Registra informações do sistema"""
        logger = get_logger('SystemInfo')
        logger.info("=== Informações do Sistema ===")
        for key, value in system_info.items():
            logger.info(f"{key}: {value}")
            
    @staticmethod
    def log_error(error, context=None):
        """Registra erros com contexto adicional"""
        logger = get_logger('Error')
        if context:
            logger.error(f"Erro em {context}: {str(error)}")
        else:
            logger.error(str(error))
            
    @staticmethod
    def log_backup_operation(operation, status, details=None):
        """Registra operações de backup"""
        logger = get_logger('Backup')
        message = f"Backup {operation}: {status}"
        if details:
            message += f" - {details}"
        logger.info(message)
        
    @staticmethod
    def log_cleanup_operation(operation, status, details=None):
        """Registra operações de limpeza"""
        logger = get_logger('Cleanup')
        message = f"Limpeza {operation}: {status}"
        if details:
            message += f" - {details}"
        logger.info(message)
        
    @staticmethod
    def log_security_event(event_type, details):
        """Registra eventos de segurança"""
        logger = get_logger('Security')
        logger.warning(f"Evento de Segurança - {event_type}: {details}")
        
    @staticmethod
    def log_performance_metrics(metrics):
        """Registra métricas de desempenho"""
        logger = get_logger('Performance')
        logger.info("=== Métricas de Desempenho ===")
        for metric, value in metrics.items():
            logger.info(f"{metric}: {value}")
            
    @staticmethod
    def export_logs(start_date=None, end_date=None, level=None):
        """Exporta logs para um arquivo"""
        try:
            log_path = get_log_path()
            export_path = log_path.parent / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            with open(log_path, 'r', encoding='utf-8') as source:
                logs = source.readlines()
                
            filtered_logs = []
            for log in logs:
                # Filtra por data
                if start_date or end_date:
                    try:
                        log_date = datetime.strptime(log[:19], '%Y-%m-%d %H:%M:%S')
                        if start_date and log_date < start_date:
                            continue
                        if end_date and log_date > end_date:
                            continue
                    except:
                        continue
                
                # Filtra por nível
                if level:
                    if f" - {level} - " not in log:
                        continue
                        
                filtered_logs.append(log)
                
            with open(export_path, 'w', encoding='utf-8') as target:
                target.writelines(filtered_logs)
                
            return str(export_path)
        except Exception as e:
            logger = get_logger()
            logger.error(f"Erro ao exportar logs: {e}")
            return None
            
    @staticmethod
    def clear_old_logs():
        """Remove logs antigos"""
        try:
            log_dir = get_log_path().parent
            current_time = datetime.now()
            
            for file in log_dir.glob("*.log.*"):
                # Verifica se o arquivo é mais antigo que 30 dias
                if (current_time - datetime.fromtimestamp(file.stat().st_mtime)).days > 30:
                    file.unlink()
                    
            return True
        except Exception as e:
            logger = get_logger()
            logger.error(f"Erro ao limpar logs antigos: {e}")
            return False 