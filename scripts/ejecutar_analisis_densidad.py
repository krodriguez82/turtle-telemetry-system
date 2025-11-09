"""
Script de Ejecución: Análisis de Densidad Espacial
Genera mapas de densidad Kernel y análisis de hotspots
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analisis_densidad import procesar_analisis_densidad

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_ENTRADA = os.path.join(BASE_DIR, 'data', 'processed', 'simplificacion_dp')
DIR_SALIDA = os.path.join(BASE_DIR, 'mapas', 'densidad')

if __name__ == "__main__":
    print("="*60)
    print("ANÁLISIS DE DENSIDAD ESPACIAL")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    print(f"Directorio entrada: {DIR_ENTRADA}")
    print(f"Directorio salida: {DIR_SALIDA}\n")
    
    # Procesar
    resultados = procesar_analisis_densidad(DIR_ENTRADA, DIR_SALIDA)
    
    if resultados:
        print("\n✓ Archivos generados:")
        print(f"  - Mapa de calor interactivo (HTML)")
        print(f"  - Mapa KDE estático (PNG)")
        print(f"  - Estadísticas de hotspots (CSV)")
    else:
        print("\n❌ Error en el procesamiento")