#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Web Scraping para descargar archivos Excel del Banco Central del Paraguay
Descarga específicamente los archivos "Tabla de Bancos" y "Tabla de Financieras"
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import logging
from urllib.parse import urljoin, urlparse
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bcp_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BCPScraper:
    """Clase para realizar web scraping del Banco Central del Paraguay"""
    
    def __init__(self, base_url="https://www.bcp.gov.py"):
        self.base_url = base_url
        self.target_url = "https://www.bcp.gov.py/web/institucional/boletines-formato-macros"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page_content(self, url):
        """Obtiene el contenido HTML de una página"""
        try:
            logger.info(f"Accediendo a: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error al acceder a {url}: {e}")
            return None
    
    def find_download_links(self, soup):
        """Busca los enlaces de descarga para los archivos específicos"""
        download_links = []
        
        # Buscar todos los enlaces que contengan texto relacionado con descarga
        links = soup.find_all('a', href=True)
        
        target_files = ['tabla de bancos', 'tabla de financieras']
        
        for link in links:
            link_text = link.get_text().lower().strip()
            href = link.get('href', '')
            
            # Verificar si el enlace corresponde a uno de nuestros archivos objetivo
            for target in target_files:
                if target in link_text or any(keyword in link_text for keyword in ['bancos', 'financieras']):
                    # Verificar si es un archivo Excel
                    if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.excel']):
                        full_url = urljoin(self.base_url, href)
                        download_links.append({
                            'name': link_text.title(),
                            'url': full_url,
                            'type': 'excel'
                        })
                        logger.info(f"Encontrado archivo: {link_text} -> {full_url}")
        
        return download_links
    
    def download_file(self, url, filename, download_dir="descargas"):
        """Descarga un archivo desde una URL"""
        try:
            # Crear directorio de descarga si no existe
            os.makedirs(download_dir, exist_ok=True)
            
            logger.info(f"Descargando: {filename}")
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Determinar la extensión del archivo
            parsed_url = urlparse(url)
            file_ext = os.path.splitext(parsed_url.path)[1]
            if not file_ext:
                file_ext = '.xlsx'  # Extensión por defecto
            
            filepath = os.path.join(download_dir, f"{filename}{file_ext}")
            
            # Descargar el archivo
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"Archivo descargado exitosamente: {filepath} ({file_size} bytes)")
            return filepath
            
        except requests.RequestException as e:
            logger.error(f"Error al descargar {url}: {e}")
            return None
        except IOError as e:
            logger.error(f"Error al escribir archivo {filename}: {e}")
            return None
    
    def scrape_and_download(self):
        """Función principal que ejecuta el scraping y descarga"""
        logger.info("Iniciando proceso de scraping del BCP...")
        
        # Obtener contenido de la página
        response = self.get_page_content(self.target_url)
        if not response:
            logger.error("No se pudo acceder a la página del BCP")
            return False
        
        # Parsear HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar enlaces de descarga
        download_links = self.find_download_links(soup)
        
        if not download_links:
            logger.warning("No se encontraron archivos para descargar")
            # Intentar con una búsqueda más amplia
            self._alternative_search(soup)
            return False
        
        # Descargar archivos encontrados
        downloaded_files = []
        for link_info in download_links:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{link_info['name']}_{timestamp}"
            
            filepath = self.download_file(link_info['url'], filename)
            if filepath:
                downloaded_files.append(filepath)
            
            # Pequeña pausa entre descargas para ser respetuoso con el servidor
            time.sleep(2)
        
        if downloaded_files:
            logger.info(f"Descarga completada. Archivos descargados: {len(downloaded_files)}")
            for filepath in downloaded_files:
                logger.info(f"- {filepath}")
            return True
        else:
            logger.error("No se pudo descargar ningún archivo")
            return False
    
    def _alternative_search(self, soup):
        """Método alternativo de búsqueda si no se encuentran los archivos"""
        logger.info("Intentando búsqueda alternativa...")
        
        # Buscar todos los enlaces que puedan contener archivos Excel
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Verificar si es un archivo Excel
            if any(ext in href.lower() for ext in ['.xlsx', '.xls']):
                logger.info(f"Enlace Excel encontrado: {text} -> {href}")
    
    def run(self):
        """Ejecuta el proceso completo"""
        logger.info("=== Iniciando Bot de Web Scraping BCP ===")
        start_time = time.time()
        
        success = self.scrape_and_download()
        
        end_time = time.time()
        duration = end_time - start_time
        
        if success:
            logger.info(f"Proceso completado exitosamente en {duration:.2f} segundos")
        else:
            logger.error(f"Proceso falló después de {duration:.2f} segundos")
        
        return success

def main():
    """Función principal"""
    scraper = BCPScraper()
    scraper.run()

if __name__ == "__main__":
    main()

