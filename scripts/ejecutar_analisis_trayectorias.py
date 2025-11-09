"""
Script de Ejecución: Análisis de Trayectorias
Calcula métricas de movimiento de las trayectorias
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analisis_trayectorias import procesar_multiples_archivos

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_ENTRADA = os.path.join(BASE_DIR, 'data', 'processed', 'simplificacion_dp')
DIR_SALIDA = os.path.join(BASE_DIR, 'data', 'processed', 'metricas_trayectorias')

if __name__ == "__main__":
    print("="*60)
    print("ANÁLISIS DE TRAYECTORIAS - MÉTRICAS DE MOVIMIENTO")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    print(f"Directorio entrada: {DIR_ENTRADA}")
    print(f"Directorio salida: {DIR_SALIDA}\n")
    
    # Procesar
    df_resumen = procesar_multiples_archivos(DIR_ENTRADA, DIR_SALIDA)
    
    if df_resumen is not None:
        # Mostrar resumen
        print("\n" + "="*120)
        print("TABLA 15: MÉTRICAS DE MOVIMIENTO")
        print("="*120)
        print(df_resumen.to_string(index=False))
        print("="*120)
        
        print("\n✓ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el procesamiento")