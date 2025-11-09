"""
Script de Ejecución: Filtrado por Coherencia Biológica
Elimina puntos que generan velocidades biológicamente imposibles
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from filtrado_velocidad import procesar_multiples_archivos

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_ENTRADA = os.path.join(BASE_DIR, 'data', 'processed', 'analisis_temporal')
DIR_SALIDA = os.path.join(BASE_DIR, 'data', 'processed', 'filtrado_coherencia')

if __name__ == "__main__":
    print("="*60)
    print("FILTRADO POR COHERENCIA BIOLÓGICA")
    print("Eliminación de puntos con velocidades imposibles")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    print(f"Directorio entrada: {DIR_ENTRADA}")
    print(f"Directorio salida: {DIR_SALIDA}\n")
    
    # Procesar
    df_resumen = procesar_multiples_archivos(DIR_ENTRADA, DIR_SALIDA)
    
    if df_resumen is not None:
        print("\n✓ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el procesamiento")
