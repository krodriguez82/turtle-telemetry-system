"""
Script de Ejecución: Visualización de Trayectorias
Genera mapas HTML interactivos con Folium
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visualizacion_trayectorias import procesar_visualizaciones

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#DIR_ENTRADA = os.path.join(BASE_DIR, 'data', 'processed', 'analisis_temporal')
DIR_ENTRADA = os.path.join(BASE_DIR, 'data', 'processed', 'simplificacion_dp')
DIR_SALIDA = os.path.join(BASE_DIR, 'mapas')

if __name__ == "__main__":
    print("="*60)
    print("GENERACIÓN DE MAPAS HTML - TRAYECTORIAS")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    print(f"Directorio entrada: {DIR_ENTRADA}")
    print(f"Directorio salida: {DIR_SALIDA}\n")
    
    # Generar visualizaciones
    procesar_visualizaciones(DIR_ENTRADA, DIR_SALIDA)
    
    print("\n✓ Proceso completado exitosamente")
    print(f"\nAbre los archivos HTML en tu navegador:")
    print(f"  - {DIR_SALIDA}/mapa_XXXXXX.html (individuales)")
    print(f"  - {DIR_SALIDA}/mapa_consolidado_todas_trayectorias.html")