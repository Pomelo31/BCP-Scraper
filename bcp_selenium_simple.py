#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot simple del BCP usando Selenium
"""

import time
import os
import logging
from datetime import datetime
import tempfile
import uuid

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bcp_selenium_simple.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Intentar importar Selenium
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
    print("❌ Selenium no está disponible")

class BCPSeleniumSimple:
    """Descargador simple del BCP usando Selenium"""
    
    def __init__(self):
        self.url = "https://www.bcp.gov.py/web/institucional/boletines-formato-macros"
        self.driver = None
        self.download_dir = os.path.abspath("descargas")
        
        # Crear directorio de descarga
        os.makedirs(self.download_dir, exist_ok=True)
    
    def setup_driver(self):
        """Configura el driver de Chrome de forma simple"""
        if not SELENIUM_AVAILABLE:
            logger.error("❌ Selenium no está disponible")
            return False
        
        try:
            chrome_options = Options()
            
            # Configuraciones básicas
            chrome_options.add_argument("--headless")  # Ejecutar sin ventana visible
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")  # Necesario para headless
            chrome_options.add_argument("--remote-debugging-port=0")  # Puerto aleatorio
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # No usar directorio de datos de usuario para evitar conflictos
            # chrome_options.add_argument(f"--user-data-dir={temp_dir}")
            
            # Configurar descarga
            prefs = {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Crear driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Ejecutar script para evitar detección
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Driver de Chrome configurado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al configurar driver: {e}")
            return False
    
    def wait_for_cloudflare(self, timeout=60):
        """Espera a que Cloudflare resuelva el desafío"""
        logger.info("⏳ Esperando a que Cloudflare resuelva el desafío...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Verificar si el título cambió de "Just a moment..."
                title = self.driver.title
                if "Just a moment" not in title and title != "":
                    logger.info("✅ Cloudflare desafío resuelto")
                    return True
                
                # Verificar si hay algún elemento que indique que la página cargó
                if self.driver.find_elements(By.TAG_NAME, "body"):
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if len(body_text) > 100 and ("tabla" in body_text.lower() or "banco" in body_text.lower()):
                        logger.info("✅ Página del BCP cargada")
                        return True
                
                time.sleep(2)
                
            except Exception as e:
                logger.debug(f"Error durante espera: {e}")
                time.sleep(2)
        
        logger.warning("⚠️ Timeout esperando Cloudflare")
        return False
    
    def buscar_enlaces_descarga(self):
        """Busca enlaces de descarga en la página"""
        logger.info("🔍 Buscando enlaces de descarga...")
        
        try:
            # Esperar a que la página cargue completamente
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Buscar botones de descarga
            download_buttons = self.driver.find_elements(
                By.XPATH, 
                "//a[contains(text(), 'Descargar') or contains(text(), 'descargar') or contains(text(), 'Download')]"
            )
            
            logger.info(f"🔗 Encontrados {len(download_buttons)} botones de descarga")
            
            enlaces_encontrados = []
            
            for i, button in enumerate(download_buttons):
                try:
                    href = button.get_attribute('href')
                    text = button.text.strip()
                    
                    if href:
                        enlaces_encontrados.append({
                            'text': text,
                            'url': href,
                            'element': button
                        })
                        logger.info(f"  {i+1}. {text} -> {href}")
                    
                except Exception as e:
                    logger.debug(f"Error procesando botón {i}: {e}")
            
            return enlaces_encontrados
            
        except TimeoutException:
            logger.error("❌ Timeout esperando que la página cargue")
            return []
        except Exception as e:
            logger.error(f"❌ Error buscando enlaces: {e}")
            return []
    
    def descargar_archivo(self, enlace):
        """Descarga un archivo usando Selenium"""
        try:
            text = enlace['text']
            url = enlace['url']
            
            logger.info(f"📥 Descargando: {text}")
            logger.info(f"🔗 URL: {url}")
            
            # Navegar directamente a la URL de descarga
            self.driver.get(url)
            
            # Esperar un poco para que inicie la descarga
            time.sleep(5)
            
            logger.info(f"✅ Descarga iniciada para: {text}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error descargando {text}: {e}")
            return False
    
    def ejecutar(self):
        """Ejecuta el proceso completo"""
        logger.info("🏦 INICIANDO DESCARGADOR BCP CON SELENIUM SIMPLE")
        logger.info("=" * 60)
        
        if not self.setup_driver():
            return False
        
        try:
            # Navegar a la página
            logger.info(f"🌐 Navegando a: {self.url}")
            self.driver.get(self.url)
            
            # Esperar a que Cloudflare resuelva el desafío
            if not self.wait_for_cloudflare():
                logger.error("❌ No se pudo resolver el desafío de Cloudflare")
                return False
            
            # Buscar enlaces de descarga
            enlaces = self.buscar_enlaces_descarga()
            
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
            for enlace in enlaces_objetivo:
                if self.descargar_archivo(enlace):
                    descargas_exitosas += 1
                time.sleep(3)  # Pausa entre descargas
            
            logger.info(f"✅ Descargas completadas: {descargas_exitosas}/{len(enlaces_objetivo)}")
            return descargas_exitosas > 0
            
        except Exception as e:
            logger.error(f"❌ Error durante la ejecución: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("🔚 Driver cerrado")

def main():
    """Función principal"""
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium no está disponible")
        print("💡 Instálalo con: pip install selenium")
        return
    
    descargador = BCPSeleniumSimple()
    success = descargador.ejecutar()
    
    if success:
        print("\n🎉 ¡Descarga completada exitosamente!")
        print("📁 Los archivos se guardaron en el directorio 'descargas/'")
    else:
        print("\n❌ La descarga falló")

if __name__ == "__main__":
    main()
