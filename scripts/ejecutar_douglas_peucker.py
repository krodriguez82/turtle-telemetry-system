"""
Script de Ejecución: Simplificación Douglas-Peucker
Simplifica trayectorias eliminando puntos redundantes
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simplificacion_douglas_peucker import procesar_multiples_archivos

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_ENTRADA = os.path.join(BASE_DIR, 'data', 'processed', 'filtrado_coherencia')
DIR_SALIDA = os.path.join(BASE_DIR, 'data', 'processed', 'simplificacion_dp')

# Tolerancia en metros (500m comparable a precisión LC1)
EPSILON = 500.0

if __name__ == "__main__":
    print("="*60)
    print("SIMPLIFICACIÓN DOUGLAS-PEUCKER")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    print(f"Directorio entrada: {DIR_ENTRADA}")
    print(f"Directorio salida: {DIR_SALIDA}\n")
    
    # Procesar
    df_resumen = procesar_multiples_archivos(DIR_ENTRADA, DIR_SALIDA, epsilon=EPSILON)
    
    if df_resumen is not None:
        # Mostrar resumen
        print("\n" + "="*80)
        print("TABLA 18: RESULTADOS DE SIMPLIFICACIÓN DOUGLAS-PEUCKER")
        print("="*80)
        print(df_resumen.to_string(index=False))
        print("="*80)
        
        print("\n✓ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el procesamiento")