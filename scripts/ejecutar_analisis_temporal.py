"""
Script de Ejecución: Análisis y Corrección Temporal
Analiza consistencia temporal, elimina duplicados y corrige datos
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analisis_temporal import procesar_multiples_archivos

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_ESPACIAL = os.path.join(BASE_DIR, 'data', 'processed', 'filtrado_espacial')
DIR_SALIDA = os.path.join(BASE_DIR, 'data', 'processed', 'analisis_temporal')

if __name__ == "__main__":
    print("="*60)
    print("ANÁLISIS Y CORRECCIÓN TEMPORAL")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    print(f"Directorio entrada: {DIR_ESPACIAL}")
    print(f"Directorio salida: {DIR_SALIDA}\n")
    
    # Procesar
    df_resumen = procesar_multiples_archivos(DIR_ESPACIAL, DIR_SALIDA)
    
    if df_resumen is not None:
        # Mostrar resumen
        print("\n" + "="*120)
        print("TABLA 16: CORRECCIÓN TEMPORAL")
        print("="*120)
        print(df_resumen.to_string(index=False))
        print("="*120)
        
        print("\n✓ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el procesamiento")