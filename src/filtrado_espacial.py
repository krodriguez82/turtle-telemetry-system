"""
Módulo: Filtrado Espacial (Eliminación de puntos en tierra y coordenadas inválidas)
Descripción: Elimina coordenadas terrestres y puntos fuera del área de estudio
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# Definir área de estudio válida (Pacífico Oriental Tropical)
LAT_MIN = 5.0    # 5°N - límite sur (sur de Panamá)
LAT_MAX = 15.0   # 15°N - límite norte (norte de Nicaragua)
LON_MIN = -95.0  # 95°W - límite oeste (costa pacífica de México/Guatemala)
LON_MAX = -75.0  # 75°W - límite este (costa pacífica de Colombia)


def cargar_poligonos_tierra(ruta_shapefile='ne_10m_land.shp'):
    """
    Carga polígonos terrestres desde shapefile de Natural Earth.
    
    Parámetros:
    - ruta_shapefile: ruta al archivo .shp (puede ser relativa o absoluta)
    """
    # Intentar varias rutas posibles
    rutas_posibles = [
        ruta_shapefile,
        os.path.join('data', ruta_shapefile),
        os.path.join('data', 'shapefiles', ruta_shapefile),
        os.path.join('..', ruta_shapefile),
    ]
    
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            try:
                tierra = gpd.read_file(ruta)
                print(f"✓ Polígonos terrestres cargados desde: {ruta}")
                print(f"  Total de polígonos: {len(tierra)}")
                return tierra
            except Exception as e:
                print(f"⚠ Error al cargar {ruta}: {e}")
    
    print(f"❌ No se encontró el archivo {ruta_shapefile}")
    print(f"   Rutas buscadas:")
    for r in rutas_posibles:
        print(f"   - {os.path.abspath(r)}")
    return None


def detectar_columnas_coordenadas(df):
    """
    Detecta automáticamente los nombres de columnas de coordenadas.
    """
    lat_col = None
    for col in df.columns:
        if 'lat' in col.lower():
            lat_col = col
            break
    
    lon_col = None
    for col in df.columns:
        if 'lon' in col.lower() or 'long' in col.lower():
            lon_col = col
            break
    
    return lat_col, lon_col


def validar_rangos_geograficos(df, lat_col, lon_col):
    """
    Valida que las coordenadas estén dentro del área de estudio.
    
    Elimina puntos fuera de:
    - Latitud: 5°N a 15°N
    - Longitud: -95°W a -75°W
    
    Retorna:
    - DataFrame filtrado
    - Número de puntos eliminados
    """
    inicial = len(df)
    
    # Filtrar coordenadas dentro del área válida
    df_valido = df[
        (df[lat_col] >= LAT_MIN) & (df[lat_col] <= LAT_MAX) &
        (df[lon_col] >= LON_MIN) & (df[lon_col] <= LON_MAX)
    ].copy()
    
    eliminados = inicial - len(df_valido)
    
    return df_valido, eliminados


def is_on_land(lat, lon, coastlines):
    """
    Verifica si un punto está en tierra.
    
    Parámetros:
    - lat: latitud
    - lon: longitud
    - coastlines: GeoDataFrame con polígonos terrestres
    
    Retorna:
    - True si el punto está en tierra, False si está en mar
    """
    point = Point(lon, lat)
    return coastlines.contains(point).any()


def filtrar_puntos_tierra(archivo_csv, poligonos_tierra):
    """
    Filtra puntos que:
    1. Están fuera del área de estudio válida
    2. Caen en tierra firme
    """
    
    print(f"\nProcesando: {os.path.basename(archivo_csv)}")
    
    # Leer CSV
    df = pd.read_csv(archivo_csv)
    df.columns = df.columns.str.strip()
    
    # Detectar columnas de coordenadas
    lat_col, lon_col = detectar_columnas_coordenadas(df)
    
    if lat_col is None or lon_col is None:
        print(f"  ❌ No se encontraron columnas de coordenadas")
        return None, None
    
    print(f"  Columnas detectadas: {lat_col}, {lon_col}")
    
    # Obtener ID del transmisor
    transmisor_id = os.path.basename(archivo_csv).split('_')[0]
    total_entrada = len(df)
    
    # Filtrar filas con coordenadas nulas
    df = df.dropna(subset=[lat_col, lon_col]).copy()
    
    nulos = total_entrada - len(df)
    if nulos > 0:
        print(f"  ⚠ {nulos} registros con coordenadas nulas eliminados")
    
    # NUEVO: Validar rangos geográficos
    df_rango_valido, fuera_rango = validar_rangos_geograficos(df, lat_col, lon_col)
    
    if fuera_rango > 0:
        print(f"  🔴 {fuera_rango} puntos FUERA del área de estudio eliminados")
        print(f"     Área válida: Lat {LAT_MIN}°-{LAT_MAX}°N, Lon {LON_MIN}°-{LON_MAX}°W")
    
    # Continuar con filtrado de tierra
    if poligonos_tierra is None:
        print(f"  ⚠ Sin polígonos terrestres, no se filtra tierra")
        return df_rango_valido, {
            'transmisor_id': transmisor_id,
            'post_calidad': total_entrada,
            'fuera_rango': fuera_rango,
            'puntos_tierra': 0,
            'puntos_mar': len(df_rango_valido),
            'porcentaje_tierra': 0.0
        }
    
    # Aplicar filtro de tierra
    print(f"  Verificando {len(df_rango_valido)} puntos en mar vs tierra...")
    
    mascara_mar = ~df_rango_valido.apply(
        lambda row: is_on_land(row[lat_col], row[lon_col], poligonos_tierra), 
        axis=1
    )
    
    df_mar = df_rango_valido[mascara_mar].copy()
    
    puntos_tierra = len(df_rango_valido) - len(df_mar)
    puntos_mar = len(df_mar)
    porcentaje_tierra = (puntos_tierra / total_entrada * 100) if total_entrada > 0 else 0
    
    estadisticas = {
        'transmisor_id': transmisor_id,
        'post_calidad': total_entrada,
        'fuera_rango': fuera_rango,
        'puntos_tierra': puntos_tierra,
        'puntos_mar': puntos_mar,
        'porcentaje_tierra': round(porcentaje_tierra, 1)
    }
    
    print(f"  Resultado:")
    print(f"    - Fuera de rango geográfico: {fuera_rango}")
    print(f"    - En tierra: {puntos_tierra} ({porcentaje_tierra:.1f}%)")
    print(f"    - En mar (retenidos): {puntos_mar}")
    
    return df_mar, estadisticas


def procesar_multiples_archivos(directorio_filtrados, directorio_salida, ruta_shapefile='ne_10m_land.shp'):
    """
    Procesa múltiples archivos y genera tabla resumen.
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Mostrar área de estudio
    print("="*60)
    print("ÁREA DE ESTUDIO DEFINIDA:")
    print(f"  Latitud: {LAT_MIN}°N a {LAT_MAX}°N")
    print(f"  Longitud: {LON_MIN}°W a {LON_MAX}°W")
    print("="*60)
    
    # Cargar polígonos terrestres
    print("\nCargando polígonos terrestres...")
    print("="*60)
    poligonos_tierra = cargar_poligonos_tierra(ruta_shapefile)
    
    if poligonos_tierra is None:
        print("\n❌ No se pueden procesar archivos sin polígonos terrestres")
        return None
    
    # Buscar archivos
    archivos = [f for f in os.listdir(directorio_filtrados) 
                if f.endswith('_filtrado_calidad.csv') and not f.startswith('Tabla')]
    
    if not archivos:
        print(f"\n❌ No se encontraron archivos en: {directorio_filtrados}")
        return None
    
    print(f"\nArchivos a procesar: {len(archivos)}")
    print("="*60)
    
    todas_estadisticas = []
    
    for archivo in archivos:
        ruta_archivo = os.path.join(directorio_filtrados, archivo)
        df_mar, stats = filtrar_puntos_tierra(ruta_archivo, poligonos_tierra)
        
        if df_mar is None:
            print(f"  ⚠ Saltando archivo por error")
            continue
        
        # Guardar
        transmisor = stats['transmisor_id']
        nombre_salida = os.path.join(directorio_salida, f"{transmisor}_filtrado_espacial.csv")
        df_mar.to_csv(nombre_salida, index=False)
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
        'post_calidad': df_resumen['post_calidad'].sum(),
        'fuera_rango': df_resumen['fuera_rango'].sum(),
        'puntos_tierra': df_resumen['puntos_tierra'].sum(),
        'puntos_mar': df_resumen['puntos_mar'].sum(),
        'porcentaje_tierra': round(
            df_resumen['puntos_tierra'].sum() / df_resumen['post_calidad'].sum() * 100, 1
        )
    }
    df_resumen = pd.concat([df_resumen, pd.DataFrame([totales])], ignore_index=True)
    
    # Guardar
    archivo_resumen = os.path.join(directorio_salida, 'Tabla11_filtrado_espacial.csv')
    df_resumen.to_csv(archivo_resumen, index=False)
    
    print("\n" + "="*60)
    print(f"✓ Tabla resumen guardada: {archivo_resumen}")
    print(f"✓ {len(archivos)} archivos procesados")
    print("="*60)
    
    return df_resumen