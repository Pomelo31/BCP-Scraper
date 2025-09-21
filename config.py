#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo de configuración para el Bot de Web Scraping del BCP
"""

# URLs del Banco Central del Paraguay
BCP_CONFIG = {
    'base_url': 'https://www.bcp.gov.py',
    'target_url': 'https://www.bcp.gov.py/web/institucional/boletines-formato-macros',
    'timeout': 30,
    'max_retries': 3
}

# Configuración de descarga
DOWNLOAD_CONFIG = {
    'download_dir': 'descargas',
    'delay_between_downloads': 2,  # segundos
    'chunk_size': 8192,
    'max_file_size': 100 * 1024 * 1024,  # 100 MB
}

# Archivos objetivo a descargar
TARGET_FILES = {
    'tabla_bancos': {
        'keywords': ['tabla de bancos', 'bancos', 'sistema bancario', 'bancos comerciales'],
        'file_extensions': ['.xlsx', '.xls', '.excel']
    },
    'tabla_financieras': {
        'keywords': ['tabla de financieras', 'financieras', 'entidades financieras', 'financieras no bancarias'],
        'file_extensions': ['.xlsx', '.xls', '.excel']
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'log_file': 'bcp_scraper.log',
    'max_log_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5
}

# Headers HTTP para simular un navegador real
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

# Configuración de reintentos
RETRY_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 2,
    'status_forcelist': [500, 502, 503, 504],
}

# Patrones regex para identificar archivos Excel
EXCEL_PATTERNS = {
    'file_extension': r'\.(xlsx|xls)$',
    'download_link': r'(descargar|download)',
    'excel_mention': r'(excel|spreadsheet|hoja.*cálculo)'
}

# Configuración de validación de archivos
VALIDATION_CONFIG = {
    'min_file_size': 1024,  # 1 KB mínimo
    'max_file_size': 100 * 1024 * 1024,  # 100 MB máximo
    'allowed_extensions': ['.xlsx', '.xls'],
    'check_content_type': True
}

