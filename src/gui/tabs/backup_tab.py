from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QProgressBar,
                            QFileDialog, QCheckBox, QSpinBox,
                            QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
import shutil
import zipfile
from datetime import datetime
from ...utils.logger import get_logger
from ...utils.config import get_config_value, update_config
from ...utils.i18n import _
from .base_tab import BaseTab

logger = get_logger('Backup')

class BackupWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, source_paths, destination, compress=True):
        super().__init__()
        self.source_paths = source_paths
        self.destination = destination
        self.compress = compress
        
    def run(self):
        try:
            # Cria pasta de backup com data
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join(self.destination, backup_name)
            
            if self.compress:
                # Backup compactado
                zip_path = f"{backup_path}.zip"
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    total_files = sum([len(files) for path in self.source_paths 
                                     for _, _, files in os.walk(path)])
                    processed_files = 0
                    
                    for source in self.source_paths:
                        for root, _, files in os.walk(source):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.dirname(source))
                                zipf.write(file_path, arcname)
                                
                                processed_files += 1
                                progress = int((processed_files / total_files) * 100)
                                self.progress.emit(progress)
                                
            else:
                # Backup normal
                os.makedirs(backup_path)
                total_files = sum([len(files) for path in self.source_paths 
                                 for _, _, files in os.walk(path)])
                processed_files = 0
                
                for source in self.source_paths:
                    dest = os.path.join(backup_path, os.path.basename(source))
                    shutil.copytree(source, dest)
                    
                    for _, _, files in os.walk(source):
                        processed_files += len(files)
                        progress = int((processed_files / total_files) * 100)
                        self.progress.emit(progress)
                        
            self.finished.emit(True, "Backup concluído com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante o backup: {e}")
            self.finished.emit(False, f"Erro durante o backup: {str(e)}")

class BackupTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Remove o layout antigo se existir
        if self.layout():
            QWidget().setLayout(self.layout())
            
        layout = QVBoxLayout()
        
        # Configurações
        self.config_group = QGroupBox()
        config_layout = QFormLayout()
        
        # Backup automático
        self.auto_backup = QCheckBox()
        self.auto_backup.setChecked(get_config_value('backup.auto_backup', False))
        self.auto_backup.stateChanged.connect(
            lambda state: update_config('backup.auto_backup', bool(state))
        )
        self.auto_backup_label = QLabel()
        config_layout.addRow(self.auto_backup_label, self.auto_backup)
        
        # Intervalo
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 168)  # 1 hora até 7 dias
        self.backup_interval.setValue(get_config_value('backup.backup_interval', 24))
        self.backup_interval.valueChanged.connect(
            lambda value: update_config('backup.backup_interval', value)
        )
        self.interval_label = QLabel()
        config_layout.addRow(self.interval_label, self.backup_interval)
        
        # Compressão
        self.compress_backup = QCheckBox()
        self.compress_backup.setChecked(get_config_value('backup.compress_backup', True))
        self.compress_backup.stateChanged.connect(
            lambda state: update_config('backup.compress_backup', bool(state))
        )
        self.compress_label = QLabel()
        config_layout.addRow(self.compress_label, self.compress_backup)
        
        self.config_group.setLayout(config_layout)
        layout.addWidget(self.config_group)
        
        # Seleção de pastas
        self.folders_group = QGroupBox()
        folders_layout = QVBoxLayout()
        
        # Desktop
        self.desktop_check = QCheckBox()
        folders_layout.addWidget(self.desktop_check)
        
        # Downloads
        self.downloads_check = QCheckBox()
        folders_layout.addWidget(self.downloads_check)
        
        # Documentos
        self.documents_check = QCheckBox()
        folders_layout.addWidget(self.documents_check)
        
        # Imagens
        self.pictures_check = QCheckBox()
        folders_layout.addWidget(self.pictures_check)
        
        self.folders_group.setLayout(folders_layout)
        layout.addWidget(self.folders_group)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.backup_btn = QPushButton()
        self.backup_btn.clicked.connect(self.start_backup)
        button_layout.addWidget(self.backup_btn)
        
        self.restore_btn = QPushButton()
        self.restore_btn.clicked.connect(self.restore_backup)
        button_layout.addWidget(self.restore_btn)
        
        layout.addLayout(button_layout)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        self.progress_bar.hide()
        
        self.setLayout(layout)
        self.update_translations()
        
    def update_translations(self):
        """Atualiza as traduções da interface"""
        self.config_group.setTitle(_("backup.settings"))
        self.auto_backup_label.setText(_("backup.auto_backup"))
        self.interval_label.setText(_("backup.interval"))
        self.compress_label.setText(_("backup.compress"))
        
        self.folders_group.setTitle(_("backup.folders"))
        self.desktop_check.setText(_("backup.desktop"))
        self.downloads_check.setText(_("backup.downloads"))
        self.documents_check.setText(_("backup.documents"))
        self.pictures_check.setText(_("backup.pictures"))
        
        self.backup_btn.setText(_("backup.start"))
        self.restore_btn.setText(_("backup.restore"))
        
    def start_backup(self):
        """Inicia o processo de backup"""
        # Verifica se alguma pasta foi selecionada
        selected_paths = []
        
        if self.desktop_check.isChecked():
            selected_paths.append(os.path.join(os.path.expanduser('~'), 'Desktop'))
            
        if self.downloads_check.isChecked():
            selected_paths.append(os.path.join(os.path.expanduser('~'), 'Downloads'))
            
        if self.documents_check.isChecked():
            selected_paths.append(os.path.join(os.path.expanduser('~'), 'Documents'))
            
        if self.pictures_check.isChecked():
            selected_paths.append(os.path.join(os.path.expanduser('~'), 'Pictures'))
            
        if not selected_paths:
            QMessageBox.warning(self, _("backup.warning"), _("backup.select_folder"))
            return
            
        # Seleciona destino do backup
        destination = QFileDialog.getExistingDirectory(
            self, _("backup.select_destination"),
            os.path.expanduser('~')
        )
        
        if destination:
            self.progress_bar.show()
            self.backup_btn.setEnabled(False)
            self.restore_btn.setEnabled(False)
            
            # Inicia o worker
            self.worker = BackupWorker(
                selected_paths,
                destination,
                self.compress_backup.isChecked()
            )
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.finished.connect(self.backup_finished)
            self.worker.start()
            
    def backup_finished(self, success, message):
        """Callback quando o backup é concluído"""
        self.progress_bar.hide()
        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, _("backup.success"), _("backup.backup_success"))
        else:
            QMessageBox.warning(self, _("backup.error"), _("backup.backup_error").format(error=message))
            
    def restore_backup(self):
        """Restaura um backup"""
        # Seleciona o backup para restaurar
        backup_file = QFileDialog.getOpenFileName(
            self, _("backup.select_backup"),
            os.path.expanduser('~'),
            "Arquivos ZIP (*.zip);;Todos os arquivos (*.*)"
        )[0]
        
        if backup_file:
            reply = QMessageBox.question(
                self,
                _("backup.confirm_restore"),
                _("backup.restore_warning"),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    # Extrai o backup
                    with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                        zip_ref.extractall(os.path.expanduser('~'))
                        
                    QMessageBox.information(self, _("backup.success"), _("backup.restore_success"))
                    
                except Exception as e:
                    logger.error(f"Erro ao restaurar backup: {e}")
                    QMessageBox.warning(self, _("backup.error"), _("backup.restore_error").format(error=str(e))) 