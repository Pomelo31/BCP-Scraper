#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot automático del BCP que intenta obtener URLs actuales automáticamente
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import logging
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bcp_auto_urls.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BCPAutoURLs:
    """Bot automático que intenta obtener URLs actuales del BCP"""
    
    def __init__(self):
        self.base_url = "https://www.bcp.gov.py"
        self.target_url = "https://www.bcp.gov.py/web/institucional/boletines-formato-macros"
        self.session = requests.Session()
        
        # URLs alternativas para probar
        self.alternative_urls = [
            "https://www.bcp.gov.py/web/institucional/boletines-formato-macros",
            "https://www.bcp.gov.py/boletines-formato-macros",
            "https://www.bcp.gov.py/web/boletines-formato-macros",
            "https://www.bcp.gov.py/institucional/boletines-formato-macros"
        ]
        
        # Patrones para encontrar URLs de archivos Excel
        self.excel_patterns = [
            r'https://www\.bcp\.gov\.py/documents/[^"]*\.xlsx[^"]*',
            r'https://www\.bcp\.gov\.py/[^"]*\.xlsx[^"]*',
            r'/[^"]*\.xlsx[^"]*',
        ]
        
        # Headers más agresivos para evitar bloqueos
        self.headers_configs = [
            {
                'name': 'Chrome Real',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                    'DNT': '1'
                }
            },
            {
                'name': 'Firefox Real',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            },
            {
                'name': 'Mobile Chrome',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive'
                }
            }
        ]
    
    def try_access_with_headers(self, url, headers_config):
        """Intenta acceder a una URL con una configuración de headers específica"""
        try:
            logger.info(f"🔍 Probando {headers_config['name']} en: {url}")
            
            self.session.headers.update(headers_config['headers'])
            response = self.session.get(url, timeout=30)
            
            logger.info(f"📊 Status: {response.status_code}")
            logger.info(f"📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
            logger.info(f"📏 Content-Length: {len(response.text):,} caracteres")
            
            if response.status_code == 200:
                logger.info(f"✅ Acceso exitoso con {headers_config['name']}")
                return response
            elif response.status_code == 403 and len(response.text) > 1000:
                logger.warning(f"⚠️ Status {response.status_code} pero con contenido ({len(response.text)} chars) - analizando...")
                return response  # Analizar el contenido aunque sea 403
            else:
                logger.warning(f"⚠️ Status {response.status_code} con {headers_config['name']}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error con {headers_config['name']}: {e}")
            return None
    
    def extract_excel_urls_from_html(self, html_content, base_url):
        """Extrae URLs de archivos Excel del contenido HTML"""
        excel_urls = []
        
        # Buscar patrones de URLs Excel
        for pattern in self.excel_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('/'):
                    full_url = urljoin(base_url, match)
                else:
                    full_url = match
                
                excel_urls.append(full_url)
        
        # Buscar enlaces con BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar todos los enlaces
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip().lower()
            
            # Si el enlace parece ser un archivo Excel
            if any(ext in href.lower() for ext in ['.xlsx', '.xls']):
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                excel_urls.append(full_url)
                logger.info(f"📊 Encontrado enlace Excel: {text} -> {full_url}")
        
        # Buscar enlaces que contengan "descargar"
        download_links = soup.find_all('a', string=re.compile(r'descargar', re.I))
        for link in download_links:
            href = link.get('href', '')
            if href:
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                excel_urls.append(full_url)
                logger.info(f"🔗 Encontrado botón descarga: {link.get_text().strip()} -> {full_url}")
        
        return list(set(excel_urls))  # Eliminar duplicados
    
    def categorize_urls(self, urls):
        """Categoriza las URLs encontradas"""
        categorized = {
            'tabla_bancos': [],
            'tabla_financieras': [],
            'otros': []
        }
        
        for url in urls:
            url_lower = url.lower()
            
            # Determinar categoría basada en la URL
            if any(keyword in url_lower for keyword in ['banco', 'bancos']):
                categorized['tabla_bancos'].append(url)
            elif any(keyword in url_lower for keyword in ['financiera', 'financieras']):
                categorized['tabla_financieras'].append(url)
            else:
                categorized['otros'].append(url)
        
        return categorized
    
    def test_url_accessibility(self, urls):
        """Prueba si las URLs son accesibles"""
        accessible_urls = []
        
        for url in urls:
            try:
                logger.info(f"🧪 Probando accesibilidad: {url}")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*'
                }
                
                response = self.session.head(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'excel' in content_type or 'spreadsheet' in content_type:
                        accessible_urls.append(url)
                        logger.info(f"✅ URL accesible: {url}")
                    else:
                        logger.warning(f"⚠️ Content-Type inesperado: {content_type}")
                else:
                    logger.warning(f"⚠️ Status {response.status_code}: {url}")
                
            except Exception as e:
                logger.error(f"❌ Error probando {url}: {e}")
            
            time.sleep(1)  # Pausa entre pruebas
        
        return accessible_urls
    
    def download_file(self, url, filename, download_dir="descargas"):
        """Descarga un archivo"""
        try:
            os.makedirs(download_dir, exist_ok=True)
            
            logger.info(f"📥 Descargando: {filename}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/octet-stream,*/*',
                'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': self.target_url
            }
            
            response = self.session.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Determinar la ruta del archivo
            filepath = os.path.join(download_dir, f"{filename}.xlsx")
            
            # Descargar el archivo
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"✅ Descargado: {filepath} ({file_size:,} bytes)")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Error descargando {filename}: {e}")
            return None
    
    def run(self):
        """Ejecuta el proceso completo"""
        logger.info("🤖 INICIANDO BOT AUTOMÁTICO BCP")
        logger.info("=" * 60)
        
        found_urls = []
        
        # Intentar diferentes URLs y headers
        for url in self.alternative_urls:
            logger.info(f"🌐 Probando URL: {url}")
            
            for headers_config in self.headers_configs:
                response = self.try_access_with_headers(url, headers_config)
                
                if response:
                    # Guardar el contenido para análisis
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"contenido_403_{timestamp}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.info(f"💾 Contenido guardado en: {filename}")
                    
                    # Extraer URLs de archivos Excel
                    excel_urls = self.extract_excel_urls_from_html(response.text, self.base_url)
                    found_urls.extend(excel_urls)
                    
                    logger.info(f"📊 URLs encontradas: {len(excel_urls)}")
                    for i, url in enumerate(excel_urls):
                        logger.info(f"  {i+1}. {url}")
                    
                    break  # Si funcionó, no probar otros headers
            
            if found_urls:
                break  # Si encontramos URLs, no probar otras URLs
        
        if not found_urls:
            logger.error("❌ No se encontraron URLs de archivos Excel")
            return False
        
        # Eliminar duplicados
        unique_urls = list(set(found_urls))
        logger.info(f"🔗 URLs únicas encontradas: {len(unique_urls)}")
        
        # Categorizar URLs
        categorized = self.categorize_urls(unique_urls)
        
        # Probar accesibilidad de URLs objetivo
        target_urls = []
        for category in ['tabla_bancos', 'tabla_financieras']:
            if categorized[category]:
                accessible = self.test_url_accessibility(categorized[category])
                target_urls.extend(accessible)
        
        if not target_urls:
            logger.warning("⚠️ No hay URLs accesibles, probando todas las encontradas")
            target_urls = self.test_url_accessibility(unique_urls[:5])  # Probar solo las primeras 5
        
        if not target_urls:
            logger.error("❌ No se encontraron URLs accesibles")
            return False
        
        # Descargar archivos
        logger.info(f"📥 Descargando {len(target_urls)} archivos...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        downloaded_files = []
        
        for i, url in enumerate(target_urls):
            filename = f"archivo_bcp_{i+1}_{timestamp}"
            filepath = self.download_file(url, filename)
            if filepath:
                downloaded_files.append(filepath)
            time.sleep(2)  # Pausa entre descargas
        
        if downloaded_files:
            logger.info(f"✅ Descarga completada: {len(downloaded_files)} archivos")
            for filepath in downloaded_files:
                logger.info(f"📁 {filepath}")
            return True
        else:
            logger.error("❌ No se pudo descargar ningún archivo")
            return False

def main():
    """Función principal"""
    bot = BCPAutoURLs()
    success = bot.run()
    
    if success:
        print("\n🎉 ¡Descarga automática completada exitosamente!")
        print("📁 Los archivos se guardaron en el directorio 'descargas/'")
    else:
        print("\n❌ La descarga automática falló")
        print("💡 El sitio puede tener protección anti-bot muy estricta")

if __name__ == "__main__":
    main()
