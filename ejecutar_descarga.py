#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para ejecutar la descarga de archivos del BCP
Versión simplificada para uso rápido
"""

import sys
import os
from datetime import datetime

def main():
    """Función principal simplificada"""
    print("🏦 Bot de Descarga - Banco Central del Paraguay")
    print("=" * 50)
    
    # Verificar que existan los archivos necesarios
    required_files = ['bcp_downloader.py', 'config.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Error: Faltan archivos necesarios: {', '.join(missing_files)}")
        return False
    
    # Importar y ejecutar el descargador
    try:
        print("📥 Iniciando descarga de archivos...")
        print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        from bcp_downloader import BCPDownloader
        
        downloader = BCPDownloader()
        success = downloader.run()
        
        print("-" * 50)
        if success:
            print("✅ ¡Descarga completada exitosamente!")
            print("📁 Los archivos se guardaron en el directorio 'descargas/'")
        else:
            print("❌ La descarga falló. Revisa los logs para más detalles.")
            print("📋 Archivos de log:")
            print("   - bcp_downloader.log")
            print("   - bcp_scraper.log")
        
        return success
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de tener todas las dependencias instaladas:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Descarga cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        sys.exit(1)

