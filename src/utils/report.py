import os
import json
from datetime import datetime
import psutil
import platform
import GPUtil
from .logger import get_logger

logger = get_logger(__name__)

def get_system_info():
    """Coleta informações do sistema para o relatório"""
    try:
        info = {
            "sistema": {
                "sistema_operacional": platform.system(),
                "versao": platform.version(),
                "arquitetura": platform.machine(),
                "processador": platform.processor(),
                "nome_computador": platform.node()
            },
            "hardware": {
                "cpu": {
                    "modelo": platform.processor(),
                    "nucleos_fisicos": psutil.cpu_count(logical=False),
                    "nucleos_logicos": psutil.cpu_count(),
                    "uso_atual": f"{psutil.cpu_percent()}%"
                },
                "memoria": {
                    "total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                    "disponivel": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
                    "uso": f"{psutil.virtual_memory().percent}%"
                }
            },
            "armazenamento": {}
        }
        
        # Informações de discos
        for disk in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(disk.mountpoint)
                info["armazenamento"][disk.device] = {
                    "ponto_montagem": disk.mountpoint,
                    "sistema_arquivos": disk.fstype,
                    "total": f"{usage.total / (1024**3):.2f} GB",
                    "usado": f"{usage.used / (1024**3):.2f} GB",
                    "livre": f"{usage.free / (1024**3):.2f} GB",
                    "uso": f"{usage.percent}%"
                }
            except:
                continue
        
        # Informações da GPU
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                info["hardware"]["gpu"] = {
                    "modelo": gpus[0].name,
                    "memoria_total": f"{gpus[0].memoryTotal} MB",
                    "memoria_usada": f"{gpus[0].memoryUsed} MB",
                    "temperatura": f"{gpus[0].temperature}°C",
                    "uso": f"{gpus[0].load * 100:.1f}%"
                }
        except:
            pass
        
        return info
        
    except Exception as e:
        logger.error(f"Erro ao coletar informações do sistema: {e}")
        return None

def generate_html_report(system_info):
    """Gera o relatório em formato HTML"""
    try:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Relatório do Sistema - ADF System Manager</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                h1, h2 {{
                    color: #333;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                }}
                .section {{
                    margin: 20px 0;
                }}
                .info-item {{
                    margin: 10px 0;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #666;
                }}
                .timestamp {{
                    color: #999;
                    font-size: 0.9em;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Relatório do Sistema - ADF System Manager</h1>
                
                <div class="section">
                    <h2>Sistema Operacional</h2>
                    <div class="info-item">
                        <span class="info-label">Sistema:</span> {system_info['sistema']['sistema_operacional']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Versão:</span> {system_info['sistema']['versao']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Arquitetura:</span> {system_info['sistema']['arquitetura']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Nome do Computador:</span> {system_info['sistema']['nome_computador']}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Hardware</h2>
                    <h3>CPU</h3>
                    <div class="info-item">
                        <span class="info-label">Modelo:</span> {system_info['hardware']['cpu']['modelo']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Núcleos Físicos:</span> {system_info['hardware']['cpu']['nucleos_fisicos']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Núcleos Lógicos:</span> {system_info['hardware']['cpu']['nucleos_logicos']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Uso Atual:</span> {system_info['hardware']['cpu']['uso_atual']}
                    </div>
                    
                    <h3>Memória</h3>
                    <div class="info-item">
                        <span class="info-label">Total:</span> {system_info['hardware']['memoria']['total']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Disponível:</span> {system_info['hardware']['memoria']['disponivel']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Uso:</span> {system_info['hardware']['memoria']['uso']}
                    </div>
                    
                    {'''
                    <h3>GPU</h3>
                    <div class="info-item">
                        <span class="info-label">Modelo:</span> {system_info['hardware']['gpu']['modelo']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Memória Total:</span> {system_info['hardware']['gpu']['memoria_total']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Memória Usada:</span> {system_info['hardware']['gpu']['memoria_usada']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Temperatura:</span> {system_info['hardware']['gpu']['temperatura']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Uso:</span> {system_info['hardware']['gpu']['uso']}
                    </div>
                    ''' if 'gpu' in system_info['hardware'] else ''}
                </div>
                
                <div class="section">
                    <h2>Armazenamento</h2>
                    {''.join(f"""
                    <h3>{device}</h3>
                    <div class="info-item">
                        <span class="info-label">Ponto de Montagem:</span> {info['ponto_montagem']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Sistema de Arquivos:</span> {info['sistema_arquivos']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Espaço Total:</span> {info['total']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Espaço Usado:</span> {info['usado']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Espaço Livre:</span> {info['livre']}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Uso:</span> {info['uso']}
                    </div>
                    """ for device, info in system_info['armazenamento'].items())}
                </div>
                
                <div class="timestamp">
                    Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório HTML: {e}")
        return None

def export_report(output_path=None):
    """Exporta o relatório do sistema"""
    try:
        # Coleta informações do sistema
        system_info = get_system_info()
        if not system_info:
            return False, "Erro ao coletar informações do sistema"
            
        # Gera o relatório HTML
        html_report = generate_html_report(system_info)
        if not html_report:
            return False, "Erro ao gerar relatório HTML"
            
        # Define o caminho de saída
        if not output_path:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            filename = f"relatorio_sistema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            output_path = os.path.join(desktop, filename)
            
        # Salva o relatório
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
            
        return True, output_path
        
    except Exception as e:
        logger.error(f"Erro ao exportar relatório: {e}")
        return False, str(e) 