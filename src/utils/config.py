"""
Módulo de gerenciamento de configurações do ADF System Manager.
"""

import json
import os
from pathlib import Path
import logging
from .constants import DEFAULT_CONFIG
from .logger import get_logger

logger = get_logger(__name__)

class Config:
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser('~'), '.adf')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.config = self.load_config()
    
    def load_config(self):
        """Carrega as configurações do arquivo"""
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Garante que a versão está atualizada
                    config['version'] = DEFAULT_CONFIG['version']
                    # Atualiza com novas configurações padrão se necessário
                    config = {**DEFAULT_CONFIG, **config}
                    # Salva as alterações
                    self.save_config(config)
                    return config
            
            # Se não existe, cria com valores padrão
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            return DEFAULT_CONFIG.copy()
    
    def save_config(self, config=None):
        """Salva as configurações no arquivo"""
        try:
            if config is not None:
                self.config = config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
                
            logger.info("Configurações salvas com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return False
    
    def get(self, key, default=None):
        """Obtém um valor da configuração"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Define um valor na configuração"""
        self.config[key] = value
        self.save_config()
    
    def __getitem__(self, key):
        return self.config[key]
    
    def __setitem__(self, key, value):
        self.config[key] = value
        self.save_config()

# Instância global
_config = Config()

def get_config():
    """Retorna a instância global de Config"""
    return _config

def get_config_path():
    """Retorna o caminho do arquivo de configuração"""
    if os.name == 'nt':  # Windows
        config_dir = os.path.join(os.getenv('APPDATA'), 'ADF')
    else:  # Linux/Mac
        config_dir = os.path.join(os.path.expanduser('~'), '.config', 'adf')
        
    # Cria o diretório se não existir
    os.makedirs(config_dir, exist_ok=True)
    
    return os.path.join(config_dir, 'config.json')

def load_config():
    """Carrega as configurações do arquivo"""
    config_path = get_config_path()
    
    try:
        # Se o arquivo existe, carrega as configurações
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Garante que a versão está sempre atualizada
            config['version'] = DEFAULT_CONFIG['version']
                
            # Atualiza com configurações padrão faltantes
            updated = False
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
                    updated = True
                elif isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if subkey not in config[key]:
                            config[key][subkey] = subvalue
                            updated = True
            
            # Se houve atualização, salva o arquivo
            if updated:
                save_config(config)
                
            return config
        
        # Se não existe, cria com configurações padrão
        else:
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
            
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Salva as configurações no arquivo"""
    try:
        config_path = get_config_path()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar configurações: {e}")
        return False

def update_config(key, value):
    """Atualiza uma configuração específica"""
    try:
        config = load_config()
        
        # Atualiza o valor
        if '.' in key:
            # Para chaves aninhadas (ex: "monitoring.cpu_threshold")
            main_key, sub_key = key.split('.')
            if main_key in config and isinstance(config[main_key], dict):
                config[main_key][sub_key] = value
        else:
            config[key] = value
        
        # Salva as alterações
        return save_config(config)
        
    except Exception as e:
        logger.error(f"Erro ao atualizar configuração: {e}")
        return False

def get_config_value(key, default=None):
    """Obtém o valor de uma configuração específica"""
    try:
        config = load_config()
        
        if '.' in key:
            main_key, sub_key = key.split('.')
            return config.get(main_key, {}).get(sub_key, default)
        
        return config.get(key, default)
        
    except Exception as e:
        logger.error(f"Erro ao obter configuração: {e}")
        return default

def reset_config():
    """Reseta as configurações para o padrão"""
    return save_config(DEFAULT_CONFIG)

def validate_config(config):
    """Valida as configurações"""
    try:
        # Verifica campos obrigatórios
        assert isinstance(config.get('version'), str), "Versão inválida"
        assert isinstance(config.get('theme'), str), "Tema inválido"
        assert isinstance(config.get('language'), str), "Idioma inválido"
        
        # Valida configurações de backup
        backup = config.get('backup', {})
        assert isinstance(backup.get('auto_backup'), bool), "Configuração de auto backup inválida"
        assert isinstance(backup.get('backup_interval'), (int, float)), "Intervalo de backup inválido"
        assert isinstance(backup.get('max_backups'), int), "Número máximo de backups inválido"
        
        # Valida configurações de monitoramento
        monitoring = config.get('monitoring', {})
        assert isinstance(monitoring.get('cpu_threshold'), (int, float)), "Limite de CPU inválido"
        assert isinstance(monitoring.get('memory_threshold'), (int, float)), "Limite de memória inválido"
        assert isinstance(monitoring.get('disk_threshold'), (int, float)), "Limite de disco inválido"
        assert isinstance(monitoring.get('network_threshold'), (int, float)), "Limite de rede inválido"
        
        return True
    except AssertionError as e:
        print(f"Erro de validação: {e}")
        return False
    except Exception as e:
        print(f"Erro ao validar configurações: {e}")
        return False

def get_all_config():
    """Retorna todas as configurações."""
    return load_config() 