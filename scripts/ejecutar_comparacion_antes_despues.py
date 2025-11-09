"""
Script de Ejecución: Comparación Antes/Después
Genera mapas comparativos de datos crudos vs procesados
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from comparacion_antes_despues import procesar_comparaciones

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_RAW = os.path.join(BASE_DIR, 'data', 'raw')
DIR_PROCESADO = os.path.join(BASE_DIR, 'data', 'processed', 'simplificacion_dp')
DIR_SALIDA = os.path.join(BASE_DIR, 'mapas', 'comparaciones')

if __name__ == "__main__":
    print("="*60)
    print("COMPARACIÓN: DATOS CRUDOS VS PROCESADOS")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    print(f"Directorio datos crudos: {DIR_RAW}")
    print(f"Directorio procesados: {DIR_PROCESADO}")
    print(f"Directorio salida: {DIR_SALIDA}\n")
    
    # None = procesar TODOS los transmisores disponibles
    # O especifica una lista: ejemplos = ['241141', '241137']
    ejemplos = None  # ← CAMBIO AQUÍ: None para procesar TODOS
    
    resultados = procesar_comparaciones(DIR_RAW, DIR_PROCESADO, DIR_SALIDA, ejemplos)
    
    print("\n✓ Proceso completado")
    print(f"\nAbre los archivos HTML en: {DIR_SALIDA}")