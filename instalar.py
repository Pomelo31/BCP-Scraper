#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de instalación para el Bot de Web Scraping del BCP
Verifica dependencias y configura el entorno
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_requirements():
    """Instala las dependencias desde requirements.txt"""
    if not os.path.exists('requirements.txt'):
        print("❌ Error: No se encontró requirements.txt")
        return False
    
    try:
        print("📦 Instalando dependencias...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Dependencias instaladas correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        print(f"   Salida: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def create_directories():
    """Crea directorios necesarios"""
    directories = ['descargas', 'logs']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Directorio creado/verificado: {directory}/")
        except Exception as e:
            print(f"❌ Error al crear directorio {directory}: {e}")
            return False
    
    return True

def verify_installation():
    """Verifica que la instalación sea correcta"""
    try:
        print("🔍 Verificando instalación...")
        
        # Verificar imports principales
        import requests
        import bs4
        print("✅ Módulos principales importados correctamente")
        
        # Verificar archivos del proyecto
        required_files = [
            'bcp_scraper.py',
            'bcp_downloader.py', 
            'config.py',
            'requirements.txt',
            'README.md'
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(f)]
        if missing_files:
            print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
            return False
        
        print("✅ Todos los archivos del proyecto presentes")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal de instalación"""
    print("🏦 Instalador - Bot de Web Scraping BCP")
    print("=" * 50)
    
    # Verificar versión de Python
    if not check_python_version():
        return False
    
    # Instalar dependencias
    if not install_requirements():
        return False
    
    # Crear directorios
    if not create_directories():
        return False
    
    # Verificar instalación
    if not verify_installation():
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ¡Instalación completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("   1. Ejecutar: python ejecutar_descarga.py")
    print("   2. O ejecutar: python bcp_downloader.py")
    print("   3. Los archivos se guardarán en: descargas/")
    print("   4. Revisar logs en caso de problemas")
    print("\n📚 Para más información, consulta README.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error crítico durante la instalación: {e}")
        sys.exit(1)

