import json
import os
from typing import Dict, Optional
from .logger import get_logger
from .config import Config

logger = get_logger(__name__)

class I18n:
    def __init__(self):
        self.config = Config()
        self.current_language = self.config.get('language', 'pt_BR')  # Carrega o idioma das configurações
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()
    
    def load_translations(self):
        """Carrega todos os arquivos de tradução disponíveis"""
        try:
            translations_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'assets', 'translations'
            )
            
            if not os.path.exists(translations_dir):
                os.makedirs(translations_dir)
            
            # Carrega cada arquivo de tradução
            for file in os.listdir(translations_dir):
                if file.endswith('.json'):
                    language = file.replace('.json', '')
                    file_path = os.path.join(translations_dir, file)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[language] = json.load(f)
                        
            logger.info(f"Traduções carregadas: {list(self.translations.keys())}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar traduções: {e}")
            # Garante que pelo menos o idioma padrão existe
            self.translations['pt_BR'] = {}
    
    def set_language(self, language: str) -> bool:
        """Define o idioma atual"""
        if language in self.translations:
            self.current_language = language
            # Salva o idioma nas configurações
            self.config.set('language', language)
            logger.info(f"Idioma alterado para: {language}")
            return True
        logger.warning(f"Idioma não disponível: {language}")
        return False
    
    def get_available_languages(self) -> list:
        """Retorna lista de idiomas disponíveis"""
        return list(self.translations.keys())
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Obtém a tradução para uma chave no idioma atual"""
        try:
            # Divide a chave em partes (para chaves aninhadas como "menu.file")
            parts = key.split('.')
            
            # Tenta obter no idioma atual
            value = self.translations[self.current_language]
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    value = None
                    break
            
            if value and isinstance(value, str):
                return value
            
            # Se não encontrar e não for pt_BR, tenta em pt_BR
            if self.current_language != 'pt_BR':
                value = self.translations['pt_BR']
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                
                if value and isinstance(value, str):
                    return value
            
            # Se ainda não encontrou, retorna o default ou a própria chave
            return default or key
            
        except Exception as e:
            logger.error(f"Erro ao obter tradução para '{key}': {e}")
            return default or key
    
    def __call__(self, key: str, default: Optional[str] = None) -> str:
        """Permite usar a instância diretamente como função"""
        return self.get(key, default)

# Instância global
_i18n = I18n()

def get_i18n() -> I18n:
    """Retorna a instância global de I18n"""
    return _i18n

# Função de conveniência
def _(key: str, default: Optional[str] = None) -> str:
    """Função de conveniência para tradução"""
    return _i18n.get(key, default) 