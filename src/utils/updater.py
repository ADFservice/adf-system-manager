import os
import json
import hashlib
import tempfile
import zipfile
import shutil
import requests
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal
from .logger import get_logger
from .config import get_config_value, update_config

logger = get_logger('Updater')

class UpdateManager:
    def __init__(self):
        self.current_version = get_config_value('version')
        self.update_url = os.path.join(os.getcwd(), "version.json")
        self.temp_dir = Path(tempfile.gettempdir()) / "ADF"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def check_for_updates(self):
        """Verifica se há atualizações disponíveis"""
        try:
            # Obtém informações da última versão
            if os.path.exists(self.update_url):
                with open(self.update_url, 'r', encoding='utf-8') as f:
                    version_info = json.load(f)
            else:
                logger.warning("Arquivo version.json não encontrado")
                return None
            
            latest_version = version_info['version']
            min_version = version_info.get('min_version', '1.0.0')
            
            # Verifica se a versão atual é suportada
            if self._compare_versions(self.current_version, min_version) < 0:
                return {
                    'available': True,
                    'required': True,
                    'version': latest_version,
                    'message': "Uma atualização obrigatória está disponível."
                }
            
            # Verifica se há uma versão mais recente
            if self._compare_versions(latest_version, self.current_version) > 0:
                return {
                    'available': True,
                    'required': version_info.get('required', False),
                    'version': latest_version,
                    'url': version_info['download_url'],
                    'notes': version_info.get('release_notes', []),
                    'hash': version_info.get('hash')
                }
            
            return {'available': False}
            
        except Exception as e:
            logger.error(f"Erro ao verificar atualizações: {e}")
            return None
            
    def _compare_versions(self, version1, version2):
        """Compara duas versões no formato x.y.z"""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
                
        return 0
        
    def download_update(self, url, version):
        """Baixa e instala a atualização"""
        try:
            # Cria diretório temporário
            update_dir = self.temp_dir / f"update_{version}"
            update_dir.mkdir(parents=True, exist_ok=True)
            
            # Baixa o arquivo
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Salva o arquivo
            update_file = update_dir / "update.zip"
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            # Extrai o arquivo
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(update_dir)
                
            # Atualiza a versão
            update_config('version', version)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao baixar atualização: {e}")
            return False
            
    def cleanup(self):
        """Limpa arquivos temporários"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários: {e}")
            
class UpdateWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def run(self):
        try:
            manager = UpdateManager()
            result = manager.check_for_updates()
            if result is None:
                self.error.emit(_("Erro ao verificar atualizações"))
            else:
                self.finished.emit(result)
        except Exception as e:
            logger.error(f"Erro ao verificar atualizações: {e}")
            self.error.emit(str(e)) 