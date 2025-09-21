#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descargador directo para archivos Excel del Banco Central del Paraguay
Versión simplificada que se enfoca en las URLs de ejemplo
"""

import requests
import os
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('descargar_directo.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DescargadorDirecto:
    """Descargador directo para archivos del BCP"""
    
    def __init__(self):
        # URLs de ejemplo (puedes actualizarlas con URLs más recientes)
        self.urls_archivos = {
            'tabla_bancos': 'https://www.bcp.gov.py/documents/20117/0/1.1+Tablas+Bolet%C3%ADn+Bancos+Jul25+%282%29+1.xlsx/c44c7087-46a1-4569-14be-32b782902f79?t=1756399940286',
            'tabla_financieras': 'https://www.bcp.gov.py/documents/20117/0/2.1+Tablas+Bolet%C3%ADn+Financieras+Jul25+%281%29+1.xlsx/64887684-ae2a-9000-e3ea-dd936598c6ef?t=1756399892013'
        }
    
    def descargar_archivo(self, url, nombre_archivo, directorio="descargas"):
        """Descarga un archivo directamente desde una URL"""
        try:
            os.makedirs(directorio, exist_ok=True)
            
            logger.info(f"📥 Descargando: {nombre_archivo}")
            logger.info(f"🔗 URL: {url}")
            
            # Headers más realistas para evitar bloqueos
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/octet-stream,*/*',
                'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.bcp.gov.py/web/institucional/boletines-formato-macros',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Hacer la petición con stream para archivos grandes
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Verificar el tipo de contenido
            content_type = response.headers.get('content-type', '').lower()
            logger.info(f"📄 Content-Type: {content_type}")
            
            # Verificar el tamaño del archivo
            content_length = response.headers.get('content-length')
            if content_length:
                logger.info(f"📏 Tamaño: {int(content_length):,} bytes")
            
            # Determinar la ruta del archivo
            filepath = os.path.join(directorio, f"{nombre_archivo}.xlsx")
            
            # Descargar el archivo
            total_size = int(content_length) if content_length else 0
            downloaded_size = 0
            
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Mostrar progreso cada MB
                        if total_size > 0 and downloaded_size % (1024 * 1024) == 0:
                            progress = (downloaded_size / total_size) * 100
                            logger.info(f"  📊 Progreso: {progress:.1f}%")
            
            # Verificar que el archivo se descargó correctamente
            file_size = os.path.getsize(filepath)
            logger.info(f"✅ Descarga completada: {filepath}")
            logger.info(f"📏 Tamaño final: {file_size:,} bytes")
            
            return filepath
            
        except requests.RequestException as e:
            logger.error(f"❌ Error de conexión: {e}")
            return None
        except IOError as e:
            logger.error(f"❌ Error al escribir archivo: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return None
    
    def probar_url(self, url, nombre):
        """Prueba si una URL es accesible"""
        try:
            logger.info(f"🧪 Probando acceso a: {nombre}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*',
                'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            # Hacer una petición HEAD para verificar sin descargar
            response = requests.head(url, headers=headers, timeout=30)
            
            logger.info(f"📊 Status: {response.status_code}")
            logger.info(f"📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
            logger.info(f"📏 Content-Length: {response.headers.get('content-length', 'N/A')}")
            
            if response.status_code == 200:
                logger.info(f"✅ {nombre}: URL accesible")
                return True
            else:
                logger.warning(f"⚠️ {nombre}: Status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {nombre}: Error - {e}")
            return False
    
    def ejecutar(self):
        """Ejecuta el proceso de descarga"""
        logger.info("🏦 DESCARGADOR DIRECTO BCP")
        logger.info("=" * 50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivos_descargados = []
        
        # Probar cada URL primero
        logger.info("🧪 PROBANDO ACCESO A URLs...")
        urls_validas = {}
        
        for nombre, url in self.urls_archivos.items():
            if self.probar_url(url, nombre):
                urls_validas[nombre] = url
            time.sleep(1)  # Pausa entre pruebas
        
        if not urls_validas:
            logger.error("❌ Ninguna URL es accesible. Las URLs pueden haber expirado.")
            logger.info("💡 Actualiza las URLs en el código con enlaces más recientes.")
            return False
        
        # Descargar archivos de URLs válidas
        logger.info(f"📥 DESCARGANDO {len(urls_validas)} ARCHIVOS...")
        
        for nombre, url in urls_validas.items():
            nombre_archivo = f"{nombre}_{timestamp}"
            filepath = self.descargar_archivo(url, nombre_archivo)
            
            if filepath:
                archivos_descargados.append(filepath)
            
            time.sleep(2)  # Pausa entre descargas
        
        # Resumen final
        logger.info("=" * 50)
        if archivos_descargados:
            logger.info(f"✅ DESCARGA COMPLETADA: {len(archivos_descargados)} archivos")
            for archivo in archivos_descargados:
                logger.info(f"  📁 {archivo}")
            return True
        else:
            logger.error("❌ No se pudo descargar ningún archivo")
            return False

def main():
    """Función principal"""
    descargador = DescargadorDirecto()
    success = descargador.ejecutar()
    
    if success:
        print("\n🎉 ¡Descarga completada exitosamente!")
        print("📁 Los archivos se guardaron en el directorio 'descargas/'")
    else:
        print("\n❌ La descarga falló.")
        print("💡 Posibles soluciones:")
        print("   - Actualiza las URLs con enlaces más recientes")
        print("   - Verifica tu conexión a internet")
        print("   - Intenta desde un navegador web primero")

if __name__ == "__main__":
    main()

