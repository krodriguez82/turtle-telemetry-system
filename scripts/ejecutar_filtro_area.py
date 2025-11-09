"""
Script de Ejecución: Filtro por Área de Estudio
Elimina puntos fuera del área geográfica esperada
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from filtro_area_estudio import procesar_multiples_archivos

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_ENTRADA = os.path.join(BASE_DIR, 'data', 'processed', 'simplificacion_dp')
DIR_SALIDA = os.path.join(BASE_DIR, 'data', 'processed', 'area_filtrada')

if __name__ == "__main__":
    print("="*60)
    print("FILTRO POR ÁREA DE ESTUDIO")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    print(f"Directorio entrada: {DIR_ENTRADA}")
    print(f"Directorio salida: {DIR_SALIDA}\n")
    
    # Procesar
    df_resumen = procesar_multiples_archivos(DIR_ENTRADA, DIR_SALIDA)
    
    if df_resumen is not None:
        # Mostrar resumen
        print("\n" + "="*80)
        print("RESUMEN DE FILTRO POR ÁREA")
        print("="*80)
        print(df_resumen.to_string(index=False))
        print("="*80)
        
        print("\n✓ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el procesamiento")