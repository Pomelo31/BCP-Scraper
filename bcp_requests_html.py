#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de descarga del BCP usando requests-html para manejar JavaScript
"""

import time
import os
import logging
from datetime import datetime
from urllib.parse import urljoin

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bcp_requests_html.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Intentar importar requests-html
try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False
    print("⚠️ requests-html no está disponible. Instálalo con: pip install requests-html")

class BCPRequestsHTML:
    """Descargador del BCP usando requests-html"""
    
    def __init__(self):
        self.url = "https://www.bcp.gov.py/web/institucional/boletines-formato-macros"
        self.session = None
        self.download_dir = os.path.abspath("descargas")
        
        # Crear directorio de descarga
        os.makedirs(self.download_dir, exist_ok=True)
    
    def setup_session(self):
        """Configura la sesión de requests-html"""
        if not REQUESTS_HTML_AVAILABLE:
            logger.error("❌ requests-html no está disponible")
            return False
        
        try:
            self.session = HTMLSession()
            
            # Headers realistas
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            logger.info("✅ Sesión requests-html configurada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al configurar sesión: {e}")
            return False
    
    def cargar_pagina(self):
        """Carga la página y maneja JavaScript"""
        try:
            logger.info(f"🌐 Cargando página: {self.url}")
            
            # Cargar la página
            response = self.session.get(self.url, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"❌ Error HTTP: {response.status_code}")
                return None
            
            logger.info("⏳ Renderizando JavaScript...")
            
            # Renderizar JavaScript (esto puede tomar tiempo)
            response.html.render(timeout=30, wait=2)
            
            logger.info("✅ Página renderizada exitosamente")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error cargando página: {e}")
            return None
    
    def buscar_enlaces_descarga(self, response):
        """Busca enlaces de descarga en la página renderizada"""
        logger.info("🔍 Buscando enlaces de descarga...")
        
        try:
            # Buscar botones de descarga
            download_buttons = response.html.find('a', containing='Descargar')
            
            logger.info(f"🔗 Encontrados {len(download_buttons)} botones de descarga")
            
            enlaces_encontrados = []
            
            for i, button in enumerate(download_buttons):
                try:
                    href = button.attrs.get('href', '')
                    text = button.text.strip()
                    
                    if href:
                        # Convertir URL relativa a absoluta
                        if href.startswith('/'):
                            href = urljoin(self.url, href)
                        
                        enlaces_encontrados.append({
                            'text': text,
                            'url': href
                        })
                        logger.info(f"  {i+1}. {text} -> {href}")
                    
                except Exception as e:
                    logger.debug(f"Error procesando botón {i}: {e}")
            
            # Buscar también enlaces directos a Excel
            excel_links = response.html.find('a[href$=".xlsx"], a[href$=".xls"]')
            
            for link in excel_links:
                try:
                    href = link.attrs.get('href', '')
                    text = link.text.strip()
                    
                    if href:
                        if href.startswith('/'):
                            href = urljoin(self.url, href)
                        
                        enlaces_encontrados.append({
                            'text': text or "Archivo Excel",
                            'url': href
                        })
                        logger.info(f"  📊 Excel: {text} -> {href}")
                
                except Exception as e:
                    logger.debug(f"Error procesando enlace Excel: {e}")
            
            return enlaces_encontrados
            
        except Exception as e:
            logger.error(f"❌ Error buscando enlaces: {e}")
            return []
    
    def descargar_archivo(self, enlace):
        """Descarga un archivo"""
        try:
            text = enlace['text']
            url = enlace['url']
            
            logger.info(f"📥 Descargando: {text}")
            logger.info(f"🔗 URL: {url}")
            
            # Headers para descarga
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*',
                'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': self.url
            }
            
            # Descargar archivo
            response = self.session.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Determinar nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{text.replace(' ', '_').replace(':', '')}_{timestamp}.xlsx"
            filepath = os.path.join(self.download_dir, filename)
            
            # Guardar archivo
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"✅ Descargado: {filepath} ({file_size:,} bytes)")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Error descargando {text}: {e}")
            return None
    
    def ejecutar(self):
        """Ejecuta el proceso completo"""
        logger.info("🏦 INICIANDO DESCARGADOR BCP CON REQUESTS-HTML")
        logger.info("=" * 60)
        
        if not self.setup_session():
            return False
        
        try:
            # Cargar página
            response = self.cargar_pagina()
            if not response:
                return False
            
            # Buscar enlaces de descarga
            enlaces = self.buscar_enlaces_descarga(response)
            
            if not enlaces:
                logger.error("❌ No se encontraron enlaces de descarga")
                return False
            
            # Filtrar enlaces objetivo
            enlaces_objetivo = []
            for enlace in enlaces:
                text = enlace['text'].lower()
                if any(keyword in text for keyword in ['tabla de bancos', 'tabla de financieras']):
                    enlaces_objetivo.append(enlace)
            
            if not enlaces_objetivo:
                logger.warning("⚠️ No se encontraron enlaces específicos, usando todos los encontrados")
                enlaces_objetivo = enlaces
            
            # Descargar archivos
            logger.info(f"📥 Descargando {len(enlaces_objetivo)} archivos...")
            
            descargas_exitosas = 0
            archivos_descargados = []
            
            for enlace in enlaces_objetivo:
                filepath = self.descargar_archivo(enlace)
                if filepath:
                    descargas_exitosas += 1
                    archivos_descargados.append(filepath)
                time.sleep(2)  # Pausa entre descargas
            
            logger.info(f"✅ Descargas completadas: {descargas_exitosas}/{len(enlaces_objetivo)}")
            
            if archivos_descargados:
                logger.info("📁 Archivos descargados:")
                for archivo in archivos_descargados:
                    logger.info(f"  - {archivo}")
            
            return descargas_exitosas > 0
            
        except Exception as e:
            logger.error(f"❌ Error durante la ejecución: {e}")
            return False

def main():
    """Función principal"""
    if not REQUESTS_HTML_AVAILABLE:
        print("❌ requests-html no está disponible")
        print("💡 Instálalo con: pip install requests-html")
        return
    
    descargador = BCPRequestsHTML()
    success = descargador.ejecutar()
    
    if success:
        print("\n🎉 ¡Descarga completada exitosamente!")
        print("📁 Los archivos se guardaron en el directorio 'descargas/'")
    else:
        print("\n❌ La descarga falló")

if __name__ == "__main__":
    main()

