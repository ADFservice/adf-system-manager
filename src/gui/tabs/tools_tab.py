from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QProgressBar,
                            QMessageBox, QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
import sys
import shutil
import subprocess
import tempfile
import ctypes
import psutil
from ...utils.logger import get_logger
from .base_tab import BaseTab
from ...utils.i18n import _

logger = get_logger(__name__)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Reinicia o aplicativo com privilégios de administrador"""
    try:
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            return True
    except Exception as e:
        logger.error(f"Erro ao tentar executar como administrador: {e}")
        return False

class CleanupWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    
    def run(self):
        """Executa a limpeza de arquivos temporários"""
        try:
            space_saved = 0
            files_removed = 0
            
            # Lista de diretórios para limpar
            temp_dirs = [
                tempfile.gettempdir(),  # Temp do sistema
                os.path.join(os.getenv('LOCALAPPDATA'), 'Temp'),  # Temp do usuário
                os.path.join(os.getenv('WINDIR'), 'Temp'),  # Temp do Windows
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Windows', 'INetCache'),  # Cache IE/Edge
                os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Windows', 'Explorer'),  # Cache do Explorer
            ]
            
            total_dirs = len(temp_dirs)
            
            for i, directory in enumerate(temp_dirs, 1):
                try:
                    if os.path.exists(directory):
                        # Calcula espaço usado
                        initial_size = self.get_dir_size(directory)
                        
                        # Remove arquivos
                        for root, dirs, files in os.walk(directory, topdown=False):
                            for name in files:
                                try:
                                    file_path = os.path.join(root, name)
                                    if os.path.exists(file_path):
                                        file_size = os.path.getsize(file_path)
                                        os.unlink(file_path)
                                        space_saved += file_size
                                        files_removed += 1
                                except Exception as e:
                                    logger.warning(f"Erro ao remover arquivo {name}: {e}")
                            
                            # Remove diretórios vazios
                            for name in dirs:
                                try:
                                    dir_path = os.path.join(root, name)
                                    if os.path.exists(dir_path):
                                        os.rmdir(dir_path)
                                except Exception as e:
                                    logger.warning(f"Erro ao remover diretório {name}: {e}")
                        
                        # Calcula progresso
                        progress = int((i / total_dirs) * 100)
                        self.progress.emit(progress, f"Limpando {os.path.basename(directory)}...")
                        
                except Exception as e:
                    logger.error(f"Erro ao limpar diretório {directory}: {e}")
            
            # Emite resultado
            result = {
                'space_saved': space_saved,
                'files_removed': files_removed
            }
            self.finished.emit(result)
            
        except Exception as e:
            logger.error(f"Erro durante limpeza: {e}")
            self.finished.emit({})
    
    def get_dir_size(self, path):
        """Calcula o tamanho total de um diretório"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size

class OptimizeWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool)
    
    def run(self):
        """Executa otimizações do sistema"""
        try:
            # Lista de otimizações
            steps = [
                ("Liberando memória", self.free_memory),
                ("Otimizando processos", self.optimize_processes),
                ("Verificando disco", self.check_disk),
                ("Limpando cache DNS", self.clear_dns_cache)
            ]
            
            total_steps = len(steps)
            
            for i, (message, func) in enumerate(steps, 1):
                # Atualiza progresso
                progress = int((i / total_steps) * 100)
                self.progress.emit(progress, message)
                
                # Executa otimização
                func()
            
            self.finished.emit(True)
            
        except Exception as e:
            logger.error(f"Erro durante otimização: {e}")
            self.finished.emit(False)
    
    def free_memory(self):
        """Libera memória do sistema"""
        try:
            # Força coleta de lixo do Python
            import gc
            gc.collect()
            
            # No Windows, pode-se usar o WMI para liberar memória
            if os.name == 'nt':
                os.system('powershell -Command "Get-Process | ForEach-Object { $_.Refresh() }"')
                
        except Exception as e:
            logger.error(f"Erro ao liberar memória: {e}")
    
    def optimize_processes(self):
        """Otimiza processos do sistema"""
        try:
            # Ajusta prioridade de processos não essenciais
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    # Processos que podem ter prioridade reduzida
                    low_priority = ['chrome.exe', 'firefox.exe', 'explorer.exe']
                    if proc.info['name'] in low_priority:
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                except Exception as e:
                    logger.warning(f"Erro ao ajustar processo {proc.info['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Erro ao otimizar processos: {e}")
    
    def check_disk(self):
        """Verifica e otimiza disco"""
        try:
            if os.name == 'nt':
                # Executa chkdsk em modo de verificação
                os.system('chkdsk /f /scan')
                
                # Desfragmenta discos (apenas HDD)
                os.system('defrag /C /H /O')
                
        except Exception as e:
            logger.error(f"Erro ao verificar disco: {e}")
    
    def clear_dns_cache(self):
        """Limpa cache DNS"""
        try:
            if os.name == 'nt':
                os.system('ipconfig /flushdns')
                
        except Exception as e:
            logger.error(f"Erro ao limpar cache DNS: {e}")

class ToolsTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Remove o layout antigo se existir
        if self.layout():
            QWidget().setLayout(self.layout())
            
        layout = QVBoxLayout()
        
        # Grupo de Limpeza
        cleanup_group = QGroupBox()
        self.set_title_key(cleanup_group, "tools.cleanup_group")
        cleanup_layout = QVBoxLayout()
        
        cleanup_desc = QLabel()
        self.set_translation_key(cleanup_desc, "tools.cleanup_desc")
        cleanup_desc.setWordWrap(True)
        cleanup_layout.addWidget(cleanup_desc)
        
        self.cleanup_progress = QProgressBar()
        self.cleanup_progress.setVisible(False)
        cleanup_layout.addWidget(self.cleanup_progress)
        
        self.cleanup_status = QLabel()
        self.cleanup_status.setVisible(False)
        cleanup_layout.addWidget(self.cleanup_status)
        
        cleanup_btn = QPushButton()
        self.set_translation_key(cleanup_btn, "tools.clean_temp")
        cleanup_btn.clicked.connect(self.clean_temp_files)
        cleanup_layout.addWidget(cleanup_btn)
        
        cleanup_group.setLayout(cleanup_layout)
        layout.addWidget(cleanup_group)
        
        # Grupo de Otimização
        optimize_group = QGroupBox()
        self.set_title_key(optimize_group, "tools.optimize_group")
        optimize_layout = QVBoxLayout()
        
        optimize_desc = QLabel()
        self.set_translation_key(optimize_desc, "tools.optimize_desc")
        optimize_desc.setWordWrap(True)
        optimize_layout.addWidget(optimize_desc)
        
        self.optimize_progress = QProgressBar()
        self.optimize_progress.setVisible(False)
        optimize_layout.addWidget(self.optimize_progress)
        
        self.optimize_status = QLabel()
        self.optimize_status.setVisible(False)
        optimize_layout.addWidget(self.optimize_status)
        
        optimize_btn = QPushButton()
        self.set_translation_key(optimize_btn, "tools.optimize")
        optimize_btn.clicked.connect(self.optimize_system)
        optimize_layout.addWidget(optimize_btn)
        
        optimize_group.setLayout(optimize_layout)
        layout.addWidget(optimize_group)
        
        # Adiciona espaço flexível
        layout.addStretch()
        
        self.setLayout(layout)
        self.update_translations()
        
    def clean_temp_files(self):
        """Inicia processo de limpeza"""
        try:
            # Verifica privilégios de administrador
            if not is_admin():
                reply = QMessageBox.question(
                    self,
                    _("messages.admin_required"),
                    _("messages.run_as_admin"),
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    run_as_admin()
                    return
                else:
                    return
            
            # Inicia worker
            self.cleanup_worker = CleanupWorker()
            self.cleanup_worker.progress.connect(self.update_cleanup_progress)
            self.cleanup_worker.finished.connect(self.cleanup_finished)
            
            # Mostra progresso
            self.cleanup_progress.setVisible(True)
            self.cleanup_status.setVisible(True)
            self.cleanup_progress.setValue(0)
            
            self.cleanup_worker.start()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar limpeza: {e}")
            QMessageBox.warning(self, _("status.error"), str(e))
            
    def update_cleanup_progress(self, value, status):
        """Atualiza progresso da limpeza"""
        self.cleanup_progress.setValue(value)
        self.cleanup_status.setText(status)
        
    def cleanup_finished(self, result):
        """Chamado quando a limpeza é concluída"""
        try:
            # Oculta progresso
            self.cleanup_progress.setVisible(False)
            self.cleanup_status.setVisible(False)
            
            # Mostra resultado
            space_saved = result.get('space_saved', 0)
            files_removed = result.get('files_removed', 0)
            
            if space_saved > 0:
                space_text = self.format_size(space_saved)
                QMessageBox.information(
                    self,
                    _("status.completed"),
                    f"{_('messages.cleanup_completed')}\n"
                    f"{_('messages.space_freed')}: {space_text}\n"
                    f"{_('messages.files_removed')}: {files_removed}"
                )
            else:
                QMessageBox.information(
                    self,
                    _("status.completed"),
                    _("messages.cleanup_completed")
                )
                
        except Exception as e:
            logger.error(f"Erro ao finalizar limpeza: {e}")
            QMessageBox.warning(self, _("status.error"), str(e))
            
    def optimize_system(self):
        """Inicia processo de otimização"""
        try:
            # Verifica privilégios de administrador
            if not is_admin():
                reply = QMessageBox.question(
                    self,
                    _("messages.admin_required"),
                    _("messages.run_as_admin"),
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    run_as_admin()
                    return
                else:
                    return
            
            # Inicia worker
            self.optimize_worker = OptimizeWorker()
            self.optimize_worker.progress.connect(self.update_optimize_progress)
            self.optimize_worker.finished.connect(self.optimize_finished)
            
            # Mostra progresso
            self.optimize_progress.setVisible(True)
            self.optimize_status.setVisible(True)
            self.optimize_progress.setValue(0)
            
            self.optimize_worker.start()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar otimização: {e}")
            QMessageBox.warning(self, _("status.error"), str(e))
            
    def update_optimize_progress(self, value, status):
        """Atualiza progresso da otimização"""
        self.optimize_progress.setValue(value)
        self.optimize_status.setText(status)
        
    def optimize_finished(self, success):
        """Chamado quando a otimização é concluída"""
        try:
            # Oculta progresso
            self.optimize_progress.setVisible(False)
            self.optimize_status.setVisible(False)
            
            # Mostra resultado
            if success:
                QMessageBox.information(
                    self,
                    _("status.completed"),
                    _("messages.optimize_completed")
                )
            else:
                QMessageBox.warning(
                    self,
                    _("status.error"),
                    _("messages.operation_error")
                )
                
        except Exception as e:
            logger.error(f"Erro ao finalizar otimização: {e}")
            QMessageBox.warning(self, _("status.error"), str(e))
            
    def format_size(self, size):
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def closeEvent(self, event):
        """Garante que os workers sejam finalizados"""
        if hasattr(self, 'cleanup_worker') and self.cleanup_worker.isRunning():
            self.cleanup_worker.terminate()
            self.cleanup_worker.wait()
            
        if hasattr(self, 'optimize_worker') and self.optimize_worker.isRunning():
            self.optimize_worker.terminate()
            self.optimize_worker.wait()
            
        event.accept() 