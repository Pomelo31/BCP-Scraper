#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para obtener URLs actuales de archivos Excel del BCP
Instrucciones paso a paso para obtener las URLs correctas
"""

import webbrowser
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mostrar_instrucciones():
    """Muestra instrucciones detalladas para obtener las URLs"""
    print("🏦 INSTRUCCIONES PARA OBTENER URLs DEL BCP")
    print("=" * 60)
    print()
    print("Las URLs de ejemplo han expirado (error 403).")
    print("Para obtener URLs actuales, sigue estos pasos:")
    print()
    print("1️⃣ ABRIR LA PÁGINA DEL BCP:")
    print("   https://www.bcp.gov.py/web/institucional/boletines-formato-macros")
    print()
    print("2️⃣ BUSCAR LOS ARCHIVOS:")
    print("   - Busca la sección 'Tabla de Bancos'")
    print("   - Busca la sección 'Tabla de Financieras'")
    print()
    print("3️⃣ OBTENER LAS URLs:")
    print("   - Haz clic derecho en el botón 'Descargar'")
    print("   - Selecciona 'Copiar enlace' o 'Copy link address'")
    print("   - Pega la URL en el código")
    print()
    print("4️⃣ ACTUALIZAR EL CÓDIGO:")
    print("   - Abre el archivo 'descargar_directo.py'")
    print("   - Reemplaza las URLs en la variable 'urls_archivos'")
    print()
    print("5️⃣ EJECUTAR EL DESCARGADOR:")
    print("   python descargar_directo.py")
    print()

def abrir_pagina_bcp():
    """Abre la página del BCP en el navegador"""
    url = "https://www.bcp.gov.py/web/institucional/boletines-formato-macros"
    print(f"🌐 Abriendo página: {url}")
    
    try:
        webbrowser.open(url)
        print("✅ Página abierta en el navegador")
        return True
    except Exception as e:
        print(f"❌ Error al abrir navegador: {e}")
        return False

def crear_template_codigo():
    """Crea un template con el código actualizado"""
    template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descargador directo para archivos Excel del Banco Central del Paraguay
ACTUALIZA LAS URLs AQUÍ CON LOS ENLACES MÁS RECIENTES
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
        # ⚠️ ACTUALIZA ESTAS URLs CON LOS ENLACES MÁS RECIENTES ⚠️
        self.urls_archivos = {
            'tabla_bancos': 'AQUÍ_PEGA_LA_URL_DE_TABLA_DE_BANCOS',
            'tabla_financieras': 'AQUÍ_PEGA_LA_URL_DE_TABLA_DE_FINANCIERAS'
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
    
    def ejecutar(self):
        """Ejecuta el proceso de descarga"""
        logger.info("🏦 DESCARGADOR DIRECTO BCP")
        logger.info("=" * 50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivos_descargados = []
        
        # Descargar archivos
        logger.info("📥 DESCARGANDO ARCHIVOS...")
        
        for nombre, url in self.urls_archivos.items():
            if url.startswith('AQUÍ_PEGA'):
                logger.warning(f"⚠️ URL no configurada para: {nombre}")
                continue
                
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
        print("\\n🎉 ¡Descarga completada exitosamente!")
        print("📁 Los archivos se guardaron en el directorio 'descargas/'")
    else:
        print("\\n❌ La descarga falló.")
        print("💡 Asegúrate de haber actualizado las URLs en el código")

if __name__ == "__main__":
    main()
'''
    
    with open('descargar_directo_template.py', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("📝 Template creado: descargar_directo_template.py")
    print("   Copia este archivo y actualiza las URLs")

def main():
    """Función principal"""
    mostrar_instrucciones()
    
    print("¿Quieres que abra la página del BCP en tu navegador? (s/n): ", end="")
    respuesta = input().lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        abrir_pagina_bcp()
    
    print()
    crear_template_codigo()
    
    print()
    print("📋 RESUMEN:")
    print("1. Obtén las URLs actuales desde el navegador")
    print("2. Actualiza el archivo 'descargar_directo_template.py'")
    print("3. Ejecuta: python descargar_directo_template.py")

if __name__ == "__main__":
    main()

