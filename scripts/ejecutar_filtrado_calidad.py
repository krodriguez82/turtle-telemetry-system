"""
Script de Ejecución: Filtrado por Calidad Argos
Ejecuta el filtrado de los 8 transmisores
"""

import sys
import os

# Agregar carpeta src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from filtrado_calidad import procesar_multiples_archivos

# Rutas relativas desde la ubicación del script
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Carpeta Modulos/
DIR_RAW = os.path.join(BASE_DIR, 'data', 'raw')
DIR_PROCESSED = os.path.join(BASE_DIR, 'data', 'processed', 'filtrado_calidad')

# Lista de archivos a procesar
TRANSMISORES = ['241136', '241137', '241138', '241139', '241140', '241141', '241142', '241143']

if __name__ == "__main__":
    print("="*60)
    print("FILTRADO POR CALIDAD ARGOS")
    print("Proyecto: Tortugas Verdes - SENACYT")
    print("="*60 + "\n")
    
    # Construir lista de archivos
    archivos_csv = [os.path.join(DIR_RAW, f'{trans}-Argos.csv') for trans in TRANSMISORES]
    
    # Verificar que existen
    archivos_existentes = [f for f in archivos_csv if os.path.exists(f)]
    archivos_faltantes = [f for f in archivos_csv if not os.path.exists(f)]
    
    if archivos_faltantes:
        print("⚠ ADVERTENCIA: Los siguientes archivos no se encontraron:")
        for f in archivos_faltantes:
            print(f"  - {os.path.basename(f)}")
        print()
    
    if not archivos_existentes:
        print("❌ ERROR: No se encontraron archivos CSV en:", DIR_RAW)
        sys.exit(1)
    
    print(f"Archivos encontrados: {len(archivos_existentes)}")
    print(f"Directorio entrada: {DIR_RAW}")
    print(f"Directorio salida: {DIR_PROCESSED}\n")
    
    # Procesar
    df_resumen = procesar_multiples_archivos(archivos_existentes, DIR_PROCESSED)
    
    # Mostrar resumen
    print("\nTABLA 10: RESUMEN DE FILTRADO POR CALIDAD")
    print("="*100)
    print(df_resumen.to_string(index=False))
    print("="*100)
    
    print("\n✓ Proceso completado exitosamente")