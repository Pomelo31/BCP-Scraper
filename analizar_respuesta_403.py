#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar la respuesta 403 del BCP
"""

import requests
from bs4 import BeautifulSoup
import json

def analizar_respuesta_403():
    """Analiza el contenido de la respuesta 403"""
    
    url = "https://www.bcp.gov.py/web/institucional/boletines-formato-macros"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    
    print("🔍 ANALIZANDO RESPUESTA 403 DEL BCP")
    print("=" * 50)
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"📏 Content-Length: {len(response.text):,} caracteres")
        print()
        
        # Guardar la respuesta completa
        with open('respuesta_403.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("📁 Respuesta guardada en: respuesta_403.html")
        
        # Analizar el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("🔍 ANÁLISIS DEL CONTENIDO:")
        print("-" * 30)
        
        # Buscar títulos
        titles = soup.find_all(['title', 'h1', 'h2', 'h3'])
        print(f"📋 Títulos encontrados: {len(titles)}")
        for title in titles[:5]:
            text = title.get_text().strip()
            if text:
                print(f"  - {text}")
        
        # Buscar mensajes de error
        error_messages = soup.find_all(string=lambda text: text and ('error' in text.lower() or 'forbidden' in text.lower() or 'blocked' in text.lower()))
        print(f"\n❌ Mensajes de error: {len(error_messages)}")
        for msg in error_messages[:3]:
            print(f"  - {msg.strip()}")
        
        # Buscar scripts que puedan contener información
        scripts = soup.find_all('script')
        print(f"\n📜 Scripts encontrados: {len(scripts)}")
        
        # Buscar enlaces que puedan ser útiles
        links = soup.find_all('a', href=True)
        print(f"\n🔗 Enlaces encontrados: {len(links)}")
        for link in links[:10]:
            href = link.get('href', '')
            text = link.get_text().strip()
            if text and ('descargar' in text.lower() or 'download' in text.lower() or 'excel' in text.lower() or '.xlsx' in href.lower()):
                print(f"  - {text} -> {href}")
        
        # Buscar formularios
        forms = soup.find_all('form')
        print(f"\n📝 Formularios encontrados: {len(forms)}")
        for form in forms:
            action = form.get('action', '')
            method = form.get('method', '')
            print(f"  - Action: {action}, Method: {method}")
        
        # Buscar meta tags que puedan dar pistas
        meta_tags = soup.find_all('meta')
        print(f"\n🏷️ Meta tags encontrados: {len(meta_tags)}")
        for meta in meta_tags[:5]:
            name = meta.get('name', '') or meta.get('property', '')
            content = meta.get('content', '')
            if name and content:
                print(f"  - {name}: {content}")
        
        # Buscar cualquier mención de "tabla", "banco", "financiera"
        relevant_text = soup.find_all(string=lambda text: text and any(word in text.lower() for word in ['tabla', 'banco', 'financiera', 'excel', 'xlsx']))
        print(f"\n🎯 Texto relevante encontrado: {len(relevant_text)}")
        for text in relevant_text[:5]:
            clean_text = text.strip()
            if clean_text and len(clean_text) < 200:  # Solo texto corto
                print(f"  - {clean_text}")
        
        # Extraer todo el texto visible
        visible_text = soup.get_text()
        print(f"\n📄 Texto visible total: {len(visible_text):,} caracteres")
        
        # Buscar patrones específicos en el texto
        if 'cloudflare' in visible_text.lower():
            print("☁️ Detectado: Cloudflare (protección anti-bot)")
        if 'captcha' in visible_text.lower():
            print("🤖 Detectado: CAPTCHA")
        if 'javascript' in visible_text.lower():
            print("⚡ Detectado: JavaScript requerido")
        
        return soup
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def buscar_urls_alternativas(soup):
    """Busca URLs alternativas en el contenido"""
    if not soup:
        return
    
    print("\n🔍 BUSCANDO URLs ALTERNATIVAS")
    print("-" * 35)
    
    # Buscar enlaces que contengan 'bcp' o 'banco'
    links = soup.find_all('a', href=True)
    
    bcp_links = []
    for link in links:
        href = link.get('href', '')
        text = link.get_text().strip()
        
        if any(keyword in href.lower() for keyword in ['bcp', 'banco', 'central', 'boletin', 'macro']):
            bcp_links.append((text, href))
    
    print(f"🔗 Enlaces del BCP encontrados: {len(bcp_links)}")
    for text, href in bcp_links[:10]:
        print(f"  - {text} -> {href}")

def main():
    """Función principal"""
    soup = analizar_respuesta_403()
    buscar_urls_alternativas(soup)
    
    print("\n💡 CONCLUSIONES:")
    print("-" * 20)
    print("1. El sitio devuelve contenido HTML aunque sea 403")
    print("2. Puede contener información útil sobre cómo acceder")
    print("3. Revisa el archivo 'respuesta_403.html' para más detalles")

if __name__ == "__main__":
    main()

