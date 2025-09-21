# Bot de Web Scraping - Banco Central del Paraguay

Este proyecto contiene un bot de web scraping desarrollado en Python para descargar automáticamente archivos Excel del Banco Central del Paraguay (BCP), específicamente los archivos "Tabla de Bancos" y "Tabla de Financieras" desde la página de boletines en formato macros.

## 📋 Características

- ✅ Descarga automática de archivos Excel del BCP
- ✅ Búsqueda inteligente de enlaces de descarga
- ✅ Manejo robusto de errores y reintentos
- ✅ Logging detallado de todas las operaciones
- ✅ Metadatos de descarga en formato JSON
- ✅ Respeto por el servidor con pausas entre descargas
- ✅ Múltiples estrategias de búsqueda de archivos
- ✅ Validación de archivos descargados

## 🚀 Instalación

### Prerrequisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd bcp-scraper
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar instalación**
   ```bash
   python --version
   pip list
   ```

## 📖 Uso

### Uso básico

```bash
# Ejecutar el descargador mejorado (recomendado)
python bcp_downloader.py

# Script simple para ejecución rápida
python ejecutar_descarga.py

# Bot básico (versión original)
python bcp_scraper.py
```

### Scripts disponibles

- **`bcp_downloader.py`** - **PRINCIPAL** - Versión mejorada con URLs de ejemplo como fallback
- **`ejecutar_descarga.py`** - Script simple para uso rápido
- **`bcp_scraper.py`** - Versión básica con funcionalidades fundamentales

### Opciones de configuración

Puedes modificar el archivo `config.py` para ajustar:

- URLs del BCP
- Directorio de descarga
- Tiempos de espera
- Palabras clave para búsqueda
- Configuración de logging

## 📁 Estructura del proyecto

```
bcp-scraper/
├── bcp_scraper.py          # Bot básico de scraping
├── bcp_downloader.py       # Descargador principal (recomendado)
├── ejecutar_descarga.py    # Script simple para ejecución
├── instalar.py            # Script de instalación automática
├── config.py              # Configuración del bot
├── requirements.txt       # Dependencias de Python
├── README.md             # Este archivo
├── descargas/            # Directorio donde se guardan los archivos
├── bcp_scraper.log       # Log del bot principal
├── bcp_downloader.log    # Log del descargador
└── metadata.json         # Metadatos de archivos descargados
```

## 🔧 Configuración

### Archivo config.py

El archivo `config.py` contiene todas las configuraciones personalizables:

- **BCP_CONFIG**: URLs y configuraciones del sitio web
- **DOWNLOAD_CONFIG**: Configuración de descarga
- **TARGET_FILES**: Archivos objetivo y palabras clave
- **LOGGING_CONFIG**: Configuración de logging
- **HTTP_HEADERS**: Headers HTTP para simular navegador

### Personalización

Puedes modificar las palabras clave de búsqueda en `TARGET_FILES`:

```python
TARGET_FILES = {
    'tabla_bancos': {
        'keywords': ['tabla de bancos', 'bancos', 'sistema bancario'],
        'file_extensions': ['.xlsx', '.xls', '.excel']
    },
    'tabla_financieras': {
        'keywords': ['tabla de financieras', 'financieras', 'entidades financieras'],
        'file_extensions': ['.xlsx', '.xls', '.excel']
    }
}
```

## 📊 Archivos de salida

### Directorio de descarga

Los archivos se guardan en el directorio `descargas/` con el formato:
```
descargas/
├── tabla_bancos_20231215_143022.xlsx
├── tabla_financieras_20231215_143025.xlsx
└── ...
```

### Logs

Los logs se guardan en:
- `bcp_scraper.log`: Log del bot principal
- `bcp_downloader.log`: Log del descargador mejorado

### Metadatos

El archivo `metadata.json` contiene información sobre los archivos descargados:

```json
{
  "timestamp": "2023-12-15T14:30:22.123456",
  "files": [
    {
      "filename": "tabla_bancos_20231215_143022.xlsx",
      "path": "descargas/tabla_bancos_20231215_143022.xlsx",
      "size": 245760,
      "modified": "2023-12-15T14:30:22.123456"
    }
  ]
}
```

## 🔍 Solución de problemas

### Problemas comunes

1. **Error de conexión**
   ```
   Error: No se pudo acceder a la página del BCP
   ```
   - Verificar conexión a internet
   - Verificar que la URL del BCP esté accesible
   - Revisar si hay bloqueos de firewall

2. **No se encuentran archivos**
   ```
   Warning: No se encontraron archivos para descargar
   ```
   - Verificar que la estructura de la página no haya cambiado
   - Ajustar las palabras clave en `config.py`
   - Revisar los logs para más detalles

3. **Error de permisos**
   ```
   Error: Permission denied
   ```
   - Verificar permisos de escritura en el directorio
   - Ejecutar con permisos de administrador si es necesario

### Debugging

Para obtener más información de debug:

1. Cambiar el nivel de logging en `config.py`:
   ```python
   LOGGING_CONFIG = {
       'level': 'DEBUG',  # Cambiar de INFO a DEBUG
       ...
   }
   ```

2. Revisar los logs detallados en los archivos `.log`

## ⚠️ Consideraciones importantes

### Ética y términos de uso

- **Respeta los términos de uso** del sitio web del BCP
- **No sobrecargues el servidor** - el bot incluye pausas entre descargas
- **Usa con moderación** - evita ejecutar el bot muy frecuentemente
- **Verifica la legalidad** de tu uso según las regulaciones locales

### Limitaciones

- El bot depende de la estructura HTML del sitio web
- Cambios en el sitio web pueden requerir actualizaciones del código
- La velocidad de descarga depende de la conexión a internet

## 🤝 Contribuciones

Si encuentras problemas o tienes mejoras:

1. Reporta bugs en la sección de issues
2. Propón mejoras con pull requests
3. Comparte tu experiencia de uso

## 📄 Licencia

Este proyecto es de código abierto. Úsalo responsablemente y respeta los términos de uso del Banco Central del Paraguay.

## 📞 Soporte

Para soporte técnico:
- Revisa la documentación
- Consulta los logs de error
- Verifica la configuración
- Reporta problemas con detalles específicos

---

**Nota**: Este bot es una herramienta educativa y de automatización. Úsalo de manera responsable y respeta siempre los términos de uso del sitio web objetivo.
