#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot híbrido del BCP: Selenium para Cloudflare + requests para descarga
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import logging
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import tempfile
import uuid

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bcp_hibrido.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BCPHibrido:
    """Bot híbrido que usa Selenium para Cloudflare y requests para descarga"""
    
    def __init__(self):
        self.base_url = "https://www.bcp.gov.py"
        self.target_url = "https://www.bcp.gov.py/web/institucional/boletines-formato-macros"
        self.download_dir = "descargas"
        self.driver = None
        self.session = requests.Session()
        
        # Headers para requests
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        os.makedirs(self.download_dir, exist_ok=True)
    
    def setup_driver(self):
        """Configura el driver de Selenium"""
        if not SELENIUM_AVAILABLE:
            logger.error("❌ Selenium no está disponible")
            return False
        
        try:
            logger.info("🔧 Configurando Chrome Driver...")
            
            chrome_options = Options()
            
            # Configuraciones para evitar detección
            chrome_options.add_argument("--headless")  # Ejecutar sin ventana
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--remote-debugging-port=0")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Configuraciones para evitar detección de bot
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
            
            # No usar directorio de datos de usuario para evitar conflictos
            # unique_id = str(uuid.uuid4())
            # temp_dir = os.path.join(tempfile.gettempdir(), f"chrome_bcp_{unique_id}")
            # chrome_options.add_argument(f"--user-data-dir={temp_dir}")
            
            # Configurar descarga
            prefs = {
                "download.default_directory": os.path.abspath(self.download_dir),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Crear el driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Ejecutar script para evitar detección
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome Driver configurado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando driver: {e}")
            return False
    
    def get_page_with_selenium(self, url, timeout=60):
        """Obtiene el contenido de la página usando Selenium"""
        try:
            logger.info(f"🌐 Navegando a: {url}")
            
            self.driver.get(url)
            
            # Esperar a que se resuelva el Cloudflare Challenge
            logger.info("⏳ Esperando resolución de Cloudflare Challenge...")
            
            # Esperar hasta que el título cambie de "Just a moment..."
            wait = WebDriverWait(self.driver, timeout)
            
            # Esperar a que el título no sea "Just a moment..."
            wait.until(lambda driver: driver.title != "Just a moment...")
            
            # Esperar un poco más para que la página se cargue completamente
            time.sleep(5)
            
            logger.info(f"✅ Página cargada: {self.driver.title}")
            logger.info(f"📄 URL actual: {self.driver.current_url}")
            
            return self.driver.page_source
            
        except TimeoutException:
            logger.error("⏰ Timeout esperando resolución de Cloudflare")
            return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo página: {e}")
            return None
    
    def extract_excel_urls(self, html_content):
        """Extrae URLs de archivos Excel del contenido HTML"""
        excel_urls = []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar todos los enlaces
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip().lower()
            
            # Si el enlace parece ser un archivo Excel
            if any(ext in href.lower() for ext in ['.xlsx', '.xls']):
                if href.startswith('/'):
                    full_url = urljoin(self.base_url, href)
                else:
                    full_url = href
                
                excel_urls.append({
                    'url': full_url,
                    'text': link.get_text().strip(),
                    'element': link
                })
                logger.info(f"📊 Encontrado Excel: {text} -> {full_url}")
        
        # Buscar enlaces que contengan palabras clave
        keywords = ['descargar', 'download', 'tabla', 'banco', 'financiera']
        
        for keyword in keywords:
            matching_links = soup.find_all('a', string=re.compile(keyword, re.I))
            for link in matching_links:
                href = link.get('href', '')
                if href:
                    if href.startswith('/'):
                        full_url = urljoin(self.base_url, href)
                    else:
                        full_url = href
                    
                    excel_urls.append({
                        'url': full_url,
                        'text': link.get_text().strip(),
                        'element': link
                    })
                    logger.info(f"🔗 Encontrado por keyword '{keyword}': {link.get_text().strip()} -> {full_url}")
        
        # Buscar patrones de URLs en el texto
        excel_patterns = [
            r'https://www\.bcp\.gov\.py/documents/[^"\s]*\.xlsx[^"\s]*',
            r'https://www\.bcp\.gov\.py/[^"\s]*\.xlsx[^"\s]*',
        ]
        
        for pattern in excel_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                excel_urls.append({
                    'url': match,
                    'text': 'URL encontrada por patrón',
                    'element': None
                })
                logger.info(f"🔍 URL por patrón: {match}")
        
        # Eliminar duplicados
        unique_urls = []
        seen_urls = set()
        
        for item in excel_urls:
            if item['url'] not in seen_urls:
                unique_urls.append(item)
                seen_urls.add(item['url'])
        
        return unique_urls
    
    def categorize_urls(self, urls):
        """Categoriza las URLs encontradas"""
        categorized = {
            'tabla_bancos': [],
            'tabla_financieras': [],
            'otros': []
        }
        
        for item in urls:
            url = item['url']
            text = item['text'].lower()
            url_lower = url.lower()
            
            # Determinar categoría
            if any(keyword in text or keyword in url_lower for keyword in ['banco', 'bancos']):
                categorized['tabla_bancos'].append(item)
            elif any(keyword in text or keyword in url_lower for keyword in ['financiera', 'financieras']):
                categorized['tabla_financieras'].append(item)
            else:
                categorized['otros'].append(item)
        
        return categorized
    
    def download_file(self, url, filename):
        """Descarga un archivo usando requests"""
        try:
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
            filepath = os.path.join(self.download_dir, f"{filename}.xlsx")
            
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
    
    def close_driver(self):
        """Cierra el driver de Selenium"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔒 Driver cerrado")
            except Exception as e:
                logger.error(f"❌ Error cerrando driver: {e}")
    
    def run(self):
        """Ejecuta el proceso completo"""
        logger.info("🤖 INICIANDO BOT HÍBRIDO BCP")
        logger.info("=" * 60)
        
        if not self.setup_driver():
            logger.error("❌ No se pudo configurar Selenium")
            return False
        
        try:
            # Obtener contenido con Selenium
            html_content = self.get_page_with_selenium(self.target_url)
            
            if not html_content:
                logger.error("❌ No se pudo obtener el contenido de la página")
                return False
            
            # Guardar el contenido para análisis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"contenido_selenium_{timestamp}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"💾 Contenido guardado en: {filename}")
            
            # Extraer URLs de Excel
            excel_urls = self.extract_excel_urls(html_content)
            
            if not excel_urls:
                logger.error("❌ No se encontraron URLs de archivos Excel")
                return False
            
            logger.info(f"📊 URLs encontradas: {len(excel_urls)}")
            
            # Categorizar URLs
            categorized = self.categorize_urls(excel_urls)
            
            # Mostrar categorías
            for category, items in categorized.items():
                if items:
                    logger.info(f"📁 {category}: {len(items)} archivos")
                    for item in items:
                        logger.info(f"  - {item['text']}: {item['url']}")
            
            # Descargar archivos objetivo
            target_files = []
            
            # Priorizar archivos de bancos y financieras
            for category in ['tabla_bancos', 'tabla_financieras']:
                if categorized[category]:
                    for item in categorized[category]:
                        target_files.append(item)
            
            # Si no hay archivos específicos, usar los primeros encontrados
            if not target_files:
                target_files = excel_urls[:3]  # Máximo 3 archivos
            
            # Descargar archivos
            downloaded_files = []
            
            for i, item in enumerate(target_files):
                filename = f"archivo_bcp_{i+1}_{timestamp}"
                filepath = self.download_file(item['url'], filename)
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
                
        finally:
            self.close_driver()

def main():
    """Función principal"""
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium no está disponible. Instala con: pip install selenium webdriver-manager")
        return
    
    bot = BCPHibrido()
    success = bot.run()
    
    if success:
        print("\n🎉 ¡Descarga híbrida completada exitosamente!")
        print("📁 Los archivos se guardaron en el directorio 'descargas/'")
    else:
        print("\n❌ La descarga híbrida falló")
        print("💡 Revisa los logs para más detalles")

if __name__ == "__main__":
    main()
