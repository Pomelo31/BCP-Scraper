#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar diferentes estrategias de parsing del BCP
"""

import requests
from bs4 import BeautifulSoup
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_different_approaches():
    """Prueba diferentes aproximaciones para acceder al sitio"""
    
    url = "https://www.bcp.gov.py/web/institucional/boletines-formato-macros"
    
    # Diferentes configuraciones de headers
    headers_configs = [
        {
            'name': 'Chrome básico',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            }
        },
        {
            'name': 'Firefox',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
            }
        },
        {
            'name': 'Safari',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
            }
        },
        {
            'name': 'Mobile Chrome',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'
            }
        },
        {
            'name': 'Headers completos',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
        }
    ]
    
    print("🧪 PROBANDO DIFERENTES ESTRATEGIAS DE ACCESO")
    print("=" * 60)
    
    for config in headers_configs:
        print(f"\n🔍 Probando: {config['name']}")
        print("-" * 40)
        
        try:
            session = requests.Session()
            session.headers.update(config['headers'])
            
            response = session.get(url, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"📏 Content-Length: {len(response.text):,} caracteres")
            
            if response.status_code == 200:
                print("✅ ¡ACCESO EXITOSO!")
                
                # Intentar parsear el contenido
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar títulos de secciones
                headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], string=lambda text: text and ('tabla' in text.lower() or 'banco' in text.lower() or 'financiera' in text.lower()))
                print(f"📋 Headers encontrados: {len(headers)}")
                
                for i, header in enumerate(headers[:5]):  # Mostrar solo los primeros 5
                    print(f"  {i+1}. {header.get_text().strip()}")
                
                # Buscar enlaces de descarga
                download_links = soup.find_all('a', string=lambda text: text and 'descargar' in text.lower())
                print(f"🔗 Enlaces de descarga: {len(download_links)}")
                
                for i, link in enumerate(download_links[:3]):  # Mostrar solo los primeros 3
                    href = link.get('href', '')
                    print(f"  {i+1}. {link.get_text().strip()} -> {href[:80]}...")
                
                # Buscar enlaces Excel
                excel_links = soup.find_all('a', href=lambda href: href and ('.xlsx' in href.lower() or '.xls' in href.lower()))
                print(f"📊 Enlaces Excel: {len(excel_links)}")
                
                for i, link in enumerate(excel_links[:3]):  # Mostrar solo los primeros 3
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    print(f"  {i+1}. {text} -> {href[:80]}...")
                
                return session, response  # Devolver la sesión exitosa
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(2)  # Pausa entre intentos
    
    print("\n❌ Ninguna estrategia funcionó")
    return None, None

def test_alternative_urls():
    """Prueba URLs alternativas"""
    alternative_urls = [
        "https://www.bcp.gov.py/web/institucional/boletines-formato-macros",
        "https://www.bcp.gov.py/boletines-formato-macros",
        "https://www.bcp.gov.py/web/boletines-formato-macros",
        "https://www.bcp.gov.py/institucional/boletines-formato-macros"
    ]
    
    print("\n🌐 PROBANDO URLs ALTERNATIVAS")
    print("=" * 40)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    
    for url in alternative_urls:
        try:
            print(f"🔍 Probando: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ ¡URL FUNCIONA!")
                return url, response
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)
    
    return None, None

def main():
    """Función principal"""
    print("🏦 TESTING BCP PARSING STRATEGIES")
    print("=" * 60)
    
    # Probar diferentes estrategias de headers
    session, response = test_different_approaches()
    
    if not response:
        # Si no funcionó, probar URLs alternativas
        url, response = test_alternative_urls()
    
    if response and response.status_code == 200:
        print("\n🎉 ¡ÉXITO! Se encontró una forma de acceder al sitio")
        print("💡 Usa esta configuración en el bot principal")
        
        # Guardar el HTML para análisis
        with open('bcp_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("📁 HTML guardado en: bcp_page.html")
        
    else:
        print("\n❌ No se pudo acceder al sitio con ninguna estrategia")
        print("💡 El sitio puede tener protección anti-bot muy estricta")
        print("💡 Considera usar un navegador con Selenium o similar")

if __name__ == "__main__":
    main()

