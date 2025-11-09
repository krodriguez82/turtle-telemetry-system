"""
Módulo: Filtro por Área de Estudio
Descripción: Elimina puntos fuera del área geográfica esperada
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import os

# Definir bounding box del área de estudio (Pacífico de Panamá)
LAT_MIN = 6.0   # Latitud mínima (sur)
LAT_MAX = 12.0  # Latitud máxima (norte)
LON_MIN = -87.0 # Longitud mínima (oeste)
LON_MAX = -76.0 # Longitud máxima (este)

def detectar_columnas_coordenadas(df):
    """Detecta columnas de latitud y longitud"""
    lat_col = lon_col = None
    
    for col in df.columns:
        if 'lat' in col.lower():
            lat_col = col
        if 'lon' in col.lower() or 'long' in col.lower():
            lon_col = col
    
    return lat_col, lon_col


def filtrar_por_area(archivo_csv, lat_min=LAT_MIN, lat_max=LAT_MAX, 
                     lon_min=LON_MIN, lon_max=LON_MAX):
    """
    Filtra puntos fuera del área de estudio definida.
    """
    
    print(f"\nProcesando: {os.path.basename(archivo_csv)}")
    
    # Leer CSV
    df = pd.read_csv(archivo_csv)
    df.columns = df.columns.str.strip()
    
    # Detectar columnas
    lat_col, lon_col = detectar_columnas_coordenadas(df)
    
    if lat_col is None or lon_col is None:
        print(f"  ❌ No se encontraron columnas de coordenadas")
        return None, None
    
    print(f"  Columnas: {lat_col}, {lon_col}")
    
    # Obtener ID del transmisor
    transmisor_id = os.path.basename(archivo_csv).split('_')[0]
    total_original = len(df)
    
    # Aplicar filtro de área
    df_filtrado = df[
        (df[lat_col] >= lat_min) & 
        (df[lat_col] <= lat_max) & 
        (df[lon_col] >= lon_min) & 
        (df[lon_col] <= lon_max)
    ].copy()
    
    puntos_eliminados = total_original - len(df_filtrado)
    porcentaje_eliminado = (puntos_eliminados / total_original * 100) if total_original > 0 else 0
    
    # Mostrar puntos fuera del área (para debug)
    if puntos_eliminados > 0:
        puntos_fuera = df[~df.index.isin(df_filtrado.index)]
        print(f"  ⚠ Puntos fuera del área detectados:")
        for idx, row in puntos_fuera.iterrows():
            print(f"    - Lat: {row[lat_col]:.4f}, Lon: {row[lon_col]:.4f}")
    
    estadisticas = {
        'transmisor_id': transmisor_id,
        'puntos_original': total_original,
        'puntos_eliminados': puntos_eliminados,
        'puntos_retenidos': len(df_filtrado),
        'porcentaje_eliminado': round(porcentaje_eliminado, 1)
    }
    
    print(f"  Original: {total_original} puntos")
    print(f"  Eliminados: {puntos_eliminados} ({porcentaje_eliminado:.1f}%)")
    print(f"  Retenidos: {len(df_filtrado)}")
    
    return df_filtrado, estadisticas


def procesar_multiples_archivos(directorio_entrada, directorio_salida):
    """
    Procesa múltiples archivos y genera tabla resumen.
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Buscar archivos
    archivos = [f for f in os.listdir(directorio_entrada) 
                if f.endswith('_simplificado_DP.csv')]
    
    if not archivos:
        print(f"\n❌ No se encontraron archivos en: {directorio_entrada}")
        return None
    
    print(f"Archivos a procesar: {len(archivos)}")
    print(f"Área de estudio:")
    print(f"  Latitud: {LAT_MIN}° a {LAT_MAX}°")
    print(f"  Longitud: {LON_MIN}° a {LON_MAX}°")
    print("="*60)
    
    todas_estadisticas = []
    
    for archivo in archivos:
        ruta_archivo = os.path.join(directorio_entrada, archivo)
        df_filtrado, stats = filtrar_por_area(ruta_archivo)
        
        if df_filtrado is None:
            print(f"  ⚠ Saltando archivo por error")
            continue
        
        # Guardar archivo filtrado
        transmisor = stats['transmisor_id']
        nombre_salida = os.path.join(directorio_salida, f"{transmisor}_area_filtrada.csv")
        df_filtrado.to_csv(nombre_salida, index=False)
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
        'puntos_eliminados': df_resumen['puntos_eliminados'].sum(),
        'puntos_retenidos': df_resumen['puntos_retenidos'].sum(),
        'porcentaje_eliminado': round(
            df_resumen['puntos_eliminados'].sum() / df_resumen['puntos_original'].sum() * 100, 1
        )
    }
    df_resumen = pd.concat([df_resumen, pd.DataFrame([totales])], ignore_index=True)
    
    # Guardar
    archivo_resumen = os.path.join(directorio_salida, 'resumen_filtro_area.csv')
    df_resumen.to_csv(archivo_resumen, index=False)
    
    print("\n" + "="*60)
    print(f"✓ Tabla resumen guardada: {archivo_resumen}")
    print(f"✓ {len(archivos)} archivos procesados")
    print("="*60)
    
    return df_resumen