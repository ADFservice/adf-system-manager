"""
Módulo de abas da interface do ADF System Manager.
"""

from .system_tab import SystemTab
from .backup_tab import BackupTab
from .updates_tab import UpdatesTab
from .settings_tab import SettingsTab
from .documents_tab import DocumentsTab

__all__ = [
    'SystemTab',
    'BackupTab',
    'UpdatesTab',
    'SettingsTab',
    'DocumentsTab'
] 