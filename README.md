# Bot de Web Scraping - Banco Central del Paraguay

Script en Python que automatiza la descarga de los boletines "Tabla de Bancos" y "Tabla de Financieras" publicados por el BCP.

## Caracteristicas principales
- Sesion HTTP con `cloudscraper` y `requests` para sortear Cloudflare.
- Descarga directa de los dos libros XLSX mas recientes con nombres fijos (`tabla_de_bancos.xlsx`, `tabla_de_financieras.xlsx`).
- Extraccion automatica de las hojas EEFF, TC y Credito Sector a CSV (`ERBI/TCBI/CSBI` y `ERFI/TCFI/CSFI`).
- Busqueda estructurada en el HTML y fallback configurado si cambian los enlaces.
- Reintentos con backoff, validacion de tipo y tamano de archivo.

## Preparacion del entorno
1. Crear el entorno virtual (solo una vez):
   ```powershell
   python -m venv albertito
   .\albertito\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. En sesiones futuras basta con activar el venv:
   ```powershell
   .\albertito\Scripts\Activate.ps1
   ```

El repositorio ignora `albertito/` y `descargas/`, por lo que ni dependencias ni resultados se versionan.

## Ejecucion
Con el venv activo:
```powershell
python bcp_downloader.py
```
El script resuelve la sesion, detecta los enlaces y descarga los archivos. Si la pagina devuelve 403 o faltan enlaces, se usan las URLs de respaldo definidas en `BCPDownloader.fallback_urls`.

## Resultados generados
El proceso deja en `descargas/`:
- `tabla_de_bancos.xlsx`
- `tabla_de_financieras.xlsx`
- `ERBI.csv`, `TCBI.csv`, `CSBI.csv`
- `ERFI.csv`, `TCFI.csv`, `CSFI.csv`

Cada CSV replica la hoja original del Excel. Si deseas logs persistentes, redirige la salida (`python bcp_downloader.py > logs.txt`).

## Ajustes y configuracion
- Las constantes principales viven en el constructor de `BCPDownloader` (`bcp_downloader.py`).
- Modifica `fallback_urls`, cabeceras HTTP o tiempos de espera segun tus necesidades.
- Cambia las hojas exportadas alterando el diccionario `sheet_targets` de `extract_sheets_to_csv`.

## Solucion de problemas rapida
| Sintoma | Posible causa | Solucion |
| --- | --- | --- |
| `403 Forbidden` continuo | Cloudflare bloqueo la sesion | Verifica que `cloudscraper` este instalado y deja que el script reintente. Si persiste, ingresa manualmente al sitio y vuelve a ejecutar. |
| "No se encontro hoja ..." | Cambiaron los nombres de pestanas | Ajusta los keywords en `sheet_targets` para que coincidan con los nuevos titulos. |
| Error al activar el venv | Ruta con caracteres especiales | Evita `[` o `]` en la ruta base o recrea el venv tras renombrar la carpeta. |

## Comandos utiles
```powershell
# Descargar y luego limpiar resultados de prueba
python bcp_downloader.py
Remove-Item descargas\* -Force

# Actualizar dependencias del entorno virtual
pip install --upgrade -r requirements.txt
```

---
Proyecto con fines informativos. Respeta los terminos de uso del BCP y limita la frecuencia de descarga para no afectar el servicio.
