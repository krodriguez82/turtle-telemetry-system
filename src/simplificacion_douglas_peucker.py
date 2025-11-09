"""
Módulo: Simplificación Douglas-Peucker
Descripción: Simplifica trayectorias usando algoritmo Douglas-Peucker
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import numpy as np
import os
from rdp import rdp

def detectar_columnas_coordenadas(df):
    """Detecta automáticamente columnas de latitud y longitud"""
    lat_col = None
    lon_col = None
    
    for col in df.columns:
        if 'lat' in col.lower():
            lat_col = col
        if 'lon' in col.lower() or 'long' in col.lower():
            lon_col = col
    
    return lat_col, lon_col


def detectar_columna_fecha(df):
    """Detecta columna de fecha"""
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            return col
    return None


def aplicar_douglas_peucker(archivo_csv, epsilon=500.0):
    """
    Aplica algoritmo Douglas-Peucker a una trayectoria.
    
    Parámetros:
    - archivo_csv: ruta al archivo CSV con datos temporales corregidos
    - epsilon: tolerancia en metros (default: 500m)
    
    Retorna:
    - df_simplificado: DataFrame con trayectoria simplificada
    - estadisticas: diccionario con métricas
    """
    
    print(f"\nProcesando: {os.path.basename(archivo_csv)}")
    
    # Leer CSV
    df = pd.read_csv(archivo_csv)
    df.columns = df.columns.str.strip()
    
    # Detectar columnas
    lat_col, lon_col = detectar_columnas_coordenadas(df)
    fecha_col = detectar_columna_fecha(df)
    
    if lat_col is None or lon_col is None:
        print(f"  ❌ No se encontraron columnas de coordenadas")
        return None, None
    
    print(f"  Columnas: {lat_col}, {lon_col}")
    
    # Obtener ID del transmisor
    transmisor_id = os.path.basename(archivo_csv).split('_')[0]
    total_original = len(df)
    
    # Ordenar por fecha si existe columna de fecha
    if fecha_col:
        df[fecha_col] = pd.to_datetime(df[fecha_col])
        df = df.sort_values(by=fecha_col).reset_index(drop=True)
    
    # Filtrar filas con coordenadas válidas
    df_valido = df.dropna(subset=[lat_col, lon_col]).copy()
    
    if len(df_valido) < 3:
        print(f"  ⚠ Insuficientes puntos para simplificar ({len(df_valido)})")
        return df_valido, {
            'transmisor_id': transmisor_id,
            'puntos_original': total_original,
            'puntos_simplificado': len(df_valido),
            'puntos_eliminados': 0,
            'tasa_simplificacion': 0.0,
            'tasa_retencion': 100.0
        }
    
    # Preparar coordenadas para Douglas-Peucker
    coords = df_valido[[lon_col, lat_col]].values
    
    # Convertir epsilon de metros a grados (aproximado)
    # A latitud ~8°N, 1 grado ≈ 111 km
    epsilon_grados = epsilon / 111000.0
    
    # Aplicar Douglas-Peucker
    try:
        # rdp retorna índices de puntos a conservar
        mask = rdp(coords, epsilon=epsilon_grados, return_mask=True)
        
        # Filtrar usando máscara
        df_simplificado = df_valido[mask].copy()
        
        puntos_simplificado = len(df_simplificado)
        puntos_eliminados = total_original - puntos_simplificado
        tasa_simplificacion = (puntos_eliminados / total_original * 100) if total_original > 0 else 0
        tasa_retencion = (puntos_simplificado / total_original * 100) if total_original > 0 else 0
        
        estadisticas = {
            'transmisor_id': transmisor_id,
            'puntos_original': total_original,
            'puntos_simplificado': puntos_simplificado,
            'puntos_eliminados': puntos_eliminados,
            'tasa_simplificacion': round(tasa_simplificacion, 1),
            'tasa_retencion': round(tasa_retencion, 1)
        }
        
        print(f"  Original: {total_original} puntos")
        print(f"  Simplificado: {puntos_simplificado} puntos")
        print(f"  Eliminados: {puntos_eliminados} ({tasa_simplificacion:.1f}%)")
        print(f"  Retención: {tasa_retencion:.1f}%")
        
        return df_simplificado, estadisticas
        
    except Exception as e:
        print(f"  ❌ Error aplicando Douglas-Peucker: {e}")
        return None, None


def procesar_multiples_archivos(directorio_entrada, directorio_salida, epsilon=500.0):
    """
    Procesa múltiples archivos y genera tabla resumen.
    
    Parámetros:
    - directorio_entrada: donde están los archivos corregidos temporalmente
    - directorio_salida: donde guardar resultados
    - epsilon: tolerancia en metros
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Buscar archivos corregidos temporalmente
    archivos = [f for f in os.listdir(directorio_entrada) 
                if f.endswith('_filtrado_coherencia.csv')]
    
    if not archivos:
        print(f"\n❌ No se encontraron archivos en: {directorio_entrada}")
        return None
    
    print(f"Archivos a procesar: {len(archivos)}")
    print(f"Tolerancia (epsilon): {epsilon} metros")
    print("="*60)
    
    todas_estadisticas = []
    
    for archivo in archivos:
        ruta_archivo = os.path.join(directorio_entrada, archivo)
        df_simp, stats = aplicar_douglas_peucker(ruta_archivo, epsilon=epsilon)
        
        if df_simp is None:
            print(f"  ⚠ Saltando archivo por error")
            continue
        
        # Guardar archivo simplificado
        transmisor = stats['transmisor_id']
        nombre_salida = os.path.join(directorio_salida, f"{transmisor}_simplificado_DP.csv")
        df_simp.to_csv(nombre_salida, index=False)
        print(f"  ✓ Guardado: {nombre_salida}")
        
        todas_estadisticas.append(stats)
    
    if not todas_estadisticas:
        print("\n❌ No se procesaron archivos exitosamente")
        return None
    
    # Crear tabla resumen
    df_resumen = pd.DataFrame(todas_estadisticas)
    
    # Agregar totales
    totales = {
        'transmisor_id': 'TOTAL',
        'puntos_original': df_resumen['puntos_original'].sum(),
        'puntos_simplificado': df_resumen['puntos_simplificado'].sum(),
        'puntos_eliminados': df_resumen['puntos_eliminados'].sum(),
        'tasa_simplificacion': round(
            df_resumen['puntos_eliminados'].sum() / df_resumen['puntos_original'].sum() * 100, 1
        ),
        'tasa_retencion': round(
            df_resumen['puntos_simplificado'].sum() / df_resumen['puntos_original'].sum() * 100, 1
        )
    }
    df_resumen = pd.concat([df_resumen, pd.DataFrame([totales])], ignore_index=True)
    
    # Guardar
    archivo_resumen = os.path.join(directorio_salida, 'Tabla18_simplificacion_douglas_peucker.csv')
    df_resumen.to_csv(archivo_resumen, index=False)
    
    print("\n" + "="*60)
    print(f"✓ Tabla resumen guardada: {archivo_resumen}")
    print(f"✓ {len(archivos)} archivos procesados")
    print("="*60)
    
    return df_resumen