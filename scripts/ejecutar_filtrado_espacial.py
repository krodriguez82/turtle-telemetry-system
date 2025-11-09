"""
Script de Ejecución: Filtrado Espacial
Elimina puntos en tierra de los datos filtrados por calidad
Usa shapefile ne_10m_land.shp de Natural Earth
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from filtrado_espacial import procesar_multiples_archivos

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_FILTRADOS = os.path.join(BASE_DIR, 'data', 'processed', 'filtrado_calidad')
DIR_SALIDA = os.path.join(BASE_DIR, 'data', 'processed', 'filtrado_espacial')

# Ruta al shapefile (ajusta según dónde lo colocaste)
SHAPEFILE = os.path.join(BASE_DIR, 'data', 'ne_10m_land', 'ne_10m_land.shp')

if __name__ == "__main__":
    print("="*60)
    print("FILTRADO ESPACIAL - ELIMINACIÓN DE PUNTOS EN TIERRA")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("Usando shapefile: ne_10m_land.shp")
    print("="*60)
    
    # Procesar
    df_resumen = procesar_multiples_archivos(
        DIR_FILTRADOS, 
        DIR_SALIDA,
        ruta_shapefile=SHAPEFILE
    )
    
    if df_resumen is not None:
        # Mostrar resumen
        print("\n" + "="*80)
        print("TABLA 11: RESULTADOS DEL FILTRADO ESPACIAL")
        print("="*80)
        print(df_resumen.to_string(index=False))
        print("="*80)
        
        print("\n✓ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el procesamiento")
