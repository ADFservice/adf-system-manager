"""Constantes e configurações padrão do aplicativo"""

DEFAULT_CONFIG = {
    "version": "1.0.3",
    "theme": "light",
    "language": "pt_BR",
    "update_check": True,
    "monitoring": {
        "cpu_threshold": 80,
        "memory_threshold": 80,
        "disk_threshold": 90,
        "network_threshold": 80
    },
    "backup": {
        "auto_backup": True,
        "backup_interval": 24,  # horas
        "backup_path": "",
        "max_backups": 5
    },
    "cleanup": {
        "auto_cleanup": False,
        "cleanup_interval": 168,  # 7 dias em horas
        "min_free_space": 10  # GB
    },
    "logging": {
        "level": "INFO",
        "max_size": 10,  # MB
        "backup_count": 3
    },
    "security": {
        "encrypt_backups": False,
        "encryption_key": "",
        "verify_updates": True
    }
}

# Configurações do logger
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 5 