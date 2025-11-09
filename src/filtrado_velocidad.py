"""
Módulo: Filtrado por Coherencia Biológica (Velocidad y Rangos Geográficos)
Descripción: Elimina puntos que generan velocidades biológicamente imposibles
             y puntos fuera del área de estudio válida
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import numpy as np
import os
from geopy.distance import geodesic

# Umbral de velocidad máxima para tortugas verdes (km/h)
# Incluye velocidades de escape ante depredadores (hasta 30 km/h en ráfagas)
VELOCIDAD_MAXIMA = 30.0

# Área de estudio válida (Pacífico Oriental Tropical)
LAT_MIN = 5.0    # 5°N - límite sur
LAT_MAX = 15.0   # 15°N - límite norte
LON_MIN = -95.0  # 95°W - límite oeste
LON_MAX = -75.0  # 75°W - límite este


def detectar_columnas(df):
    """Detecta columnas necesarias"""
    lat_col = lon_col = fecha_col = None
    
    for col in df.columns:
        if 'lat' in col.lower():
            lat_col = col
        if 'lon' in col.lower() or 'long' in col.lower():
            lon_col = col
        if 'date' in col.lower() or 'time' in col.lower():
            fecha_col = col
    
    return lat_col, lon_col, fecha_col


def validar_rangos_geograficos(df, lat_col, lon_col):
    """
    Valida que las coordenadas estén dentro del área de estudio.
    
    Elimina puntos fuera de:
    - Latitud: 5°N a 15°N
    - Longitud: -95°W a -75°W
    
    Retorna:
    - DataFrame filtrado
    - Número de puntos eliminados
    - Lista de puntos eliminados con sus coordenadas
    """
    inicial = len(df)
    
    # Identificar puntos fuera de rango
    fuera_rango = df[
        (df[lat_col] < LAT_MIN) | (df[lat_col] > LAT_MAX) |
        (df[lon_col] < LON_MIN) | (df[lon_col] > LON_MAX)
    ]
    
    # Guardar info de puntos problemáticos
    puntos_problematicos = []
    for idx, row in fuera_rango.iterrows():
        puntos_problematicos.append({
            'indice': idx,
            'lat': row[lat_col],
            'lon': row[lon_col],
            'fecha': row.get('Date', 'N/A')
        })
    
    # Filtrar coordenadas dentro del área válida
    df_valido = df[
        (df[lat_col] >= LAT_MIN) & (df[lat_col] <= LAT_MAX) &
        (df[lon_col] >= LON_MIN) & (df[lon_col] <= LON_MAX)
    ].copy()
    
    eliminados = inicial - len(df_valido)
    
    return df_valido, eliminados, puntos_problematicos


def calcular_velocidad(p1_lat, p1_lon, p1_fecha, p2_lat, p2_lon, p2_fecha):
    """
    Calcula velocidad entre dos puntos consecutivos.
    
    Retorna:
    - velocidad en km/h
    """
    # Distancia en km
    distancia_km = geodesic((p1_lat, p1_lon), (p2_lat, p2_lon)).km
    
    # Tiempo en horas
    delta_tiempo = (p2_fecha - p1_fecha).total_seconds() / 3600
    
    if delta_tiempo <= 0:
        return 0
    
    velocidad = distancia_km / delta_tiempo
    
    return velocidad


def filtrar_por_velocidad(archivo_csv, velocidad_maxima=VELOCIDAD_MAXIMA):
    """
    Filtra puntos que:
    1. Están fuera del área de estudio válida
    2. Generan velocidades biológicamente imposibles
    """
    
    print(f"\nProcesando: {os.path.basename(archivo_csv)}")
    
    # Leer CSV
    df = pd.read_csv(archivo_csv)
    df.columns = df.columns.str.strip()
    
    # Detectar columnas
    lat_col, lon_col, fecha_col = detectar_columnas(df)
    
    if lat_col is None or lon_col is None or fecha_col is None:
        print(f"  ❌ Faltan columnas necesarias")
        return None, None
    
    print(f"  Columnas: {lat_col}, {lon_col}, {fecha_col}")
    
    # Obtener ID del transmisor
    transmisor_id = os.path.basename(archivo_csv).split('_')[0]
    
    # Convertir fecha y ordenar
    df[fecha_col] = pd.to_datetime(df[fecha_col])
    df = df.sort_values(by=fecha_col).reset_index(drop=True)
    
    # Eliminar nulos
    df = df.dropna(subset=[lat_col, lon_col, fecha_col])
    
    total_inicial = len(df)
    
    # PASO 1: Validar rangos geográficos
    print(f"  PASO 1: Validando rangos geográficos...")
    df_rango_valido, fuera_rango, puntos_prob = validar_rangos_geograficos(df, lat_col, lon_col)
    
    if fuera_rango > 0:
        print(f"  🔴 {fuera_rango} puntos FUERA del área de estudio eliminados:")
        print(f"     Área válida: Lat {LAT_MIN}°-{LAT_MAX}°N, Lon {LON_MIN}°-{LON_MAX}°W")
        for punto in puntos_prob:
            print(f"     - Punto índice {punto['indice']}: ({punto['lat']:.4f}, {punto['lon']:.4f})")
    else:
        print(f"  ✓ Todos los puntos dentro del área de estudio")
    
    # Actualizar df para el siguiente paso
    df = df_rango_valido.reset_index(drop=True)
    
    if len(df) < 2:
        print(f"  ⚠ Insuficientes puntos tras filtro geográfico ({len(df)})")
        return df, {
            'transmisor_id': transmisor_id,
            'puntos_inicial': total_inicial,
            'fuera_rango': fuera_rango,
            'segmentos_imposibles': 0,
            'puntos_eliminados_velocidad': 0,
            'puntos_final': len(df),
            'velocidad_max_detectada': 0
        }
    
    # PASO 2: Validar velocidades
    print(f"  PASO 2: Validando velocidades entre {len(df)} puntos...")
    
    puntos_a_eliminar = set()
    velocidades_imposibles = []
    velocidad_maxima_detectada = 0
    
    for i in range(len(df) - 1):
        p1 = df.iloc[i]
        p2 = df.iloc[i + 1]
        
        velocidad = calcular_velocidad(
            p1[lat_col], p1[lon_col], p1[fecha_col],
            p2[lat_col], p2[lon_col], p2[fecha_col]
        )
        
        # Rastrear velocidad máxima
        if velocidad > velocidad_maxima_detectada:
            velocidad_maxima_detectada = velocidad
        
        if velocidad > velocidad_maxima:
            # Velocidad imposible detectada
            distancia = geodesic((p1[lat_col], p1[lon_col]), 
                                (p2[lat_col], p2[lon_col])).km
            
            velocidades_imposibles.append(velocidad)
            
            print(f"  🔴 Velocidad imposible: {velocidad:.2f} km/h")
            print(f"     Entre punto {i} ({p1[fecha_col]}) y {i+1} ({p2[fecha_col]})")
            print(f"     Distancia: {distancia:.2f} km")
            print(f"     P1: ({p1[lat_col]:.4f}, {p1[lon_col]:.4f})")
            print(f"     P2: ({p2[lat_col]:.4f}, {p2[lon_col]:.4f})")
            
            # Estrategia: verificar contexto para decidir cuál punto eliminar
            
            # Calcular velocidad con punto anterior a p1 (si existe)
            if i > 0:
                vel_anterior = calcular_velocidad(
                    df.iloc[i-1][lat_col], df.iloc[i-1][lon_col], df.iloc[i-1][fecha_col],
                    p1[lat_col], p1[lon_col], p1[fecha_col]
                )
            else:
                vel_anterior = 0
            
            # Calcular velocidad con punto posterior a p2 (si existe)
            if i + 2 < len(df):
                vel_posterior = calcular_velocidad(
                    p2[lat_col], p2[lon_col], p2[fecha_col],
                    df.iloc[i+2][lat_col], df.iloc[i+2][lon_col], df.iloc[i+2][fecha_col]
                )
            else:
                vel_posterior = 0
            
            # Decidir qué punto eliminar
            if vel_anterior > velocidad_maxima:
                # p1 es problemático (también genera velocidad alta con anterior)
                puntos_a_eliminar.add(i)
                print(f"     → Eliminando P1 (índice {i}) - problemático con anterior también")
            elif vel_posterior > velocidad_maxima:
                # p2 es problemático (también genera velocidad alta con posterior)
                puntos_a_eliminar.add(i + 1)
                print(f"     → Eliminando P2 (índice {i+1}) - problemático con posterior también")
            else:
                # Ambos vecinos son normales, eliminar el punto más extremo
                # Heurística: eliminar p1 (conservador - elimina el primero del par)
                puntos_a_eliminar.add(i)
                print(f"     → Eliminando P1 (índice {i}) - heurística conservadora")
    
    # Filtrar puntos con velocidad imposible
    df_filtrado = df.drop(list(puntos_a_eliminar)).reset_index(drop=True)
    
    puntos_eliminados_velocidad = len(df) - len(df_filtrado)
    segmentos_imposibles = len(velocidades_imposibles)
    
    estadisticas = {
        'transmisor_id': transmisor_id,
        'puntos_inicial': total_inicial,
        'fuera_rango': fuera_rango,
        'segmentos_imposibles': segmentos_imposibles,
        'puntos_eliminados_velocidad': puntos_eliminados_velocidad,
        'puntos_final': len(df_filtrado),
        'velocidad_max_detectada': round(velocidad_maxima_detectada, 2) if velocidad_maxima_detectada > 0 else 0
    }
    
    print(f"  RESUMEN:")
    print(f"    - Puntos iniciales: {total_inicial}")
    print(f"    - Eliminados por rango geográfico: {fuera_rango}")
    print(f"    - Segmentos con velocidad >{velocidad_maxima} km/h: {segmentos_imposibles}")
    print(f"    - Eliminados por velocidad: {puntos_eliminados_velocidad}")
    print(f"    - Puntos finales: {len(df_filtrado)}")
    if velocidad_maxima_detectada > 0:
        print(f"    - Velocidad máxima detectada: {velocidad_maxima_detectada:.2f} km/h")
    
    return df_filtrado, estadisticas


def procesar_multiples_archivos(directorio_entrada, directorio_salida, velocidad_maxima=VELOCIDAD_MAXIMA):
    """
    Procesa múltiples archivos y genera tabla resumen.
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Buscar archivos (después de corrección temporal)
    archivos = [f for f in os.listdir(directorio_entrada) 
                if f.endswith('_corregido_temporal.csv')]
    
    if not archivos:
        print(f"\n❌ No se encontraron archivos en: {directorio_entrada}")
        return None
    
    print(f"Archivos a procesar: {len(archivos)}")
    print(f"Velocidad máxima permitida: {velocidad_maxima} km/h")
    print(f"Área de estudio: Lat {LAT_MIN}°-{LAT_MAX}°N, Lon {LON_MIN}°-{LON_MAX}°W")
    print("="*60)
    
    todas_estadisticas = []
    
    for archivo in archivos:
        ruta_archivo = os.path.join(directorio_entrada, archivo)
        df_filtrado, stats = filtrar_por_velocidad(ruta_archivo, velocidad_maxima)
        
        if df_filtrado is None:
            print(f"  ⚠ Saltando archivo por error")
            continue
        
        # Guardar
        transmisor = stats['transmisor_id']
        nombre_salida = os.path.join(directorio_salida, f"{transmisor}_filtrado_coherencia.csv")
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
        'puntos_inicial': df_resumen['puntos_inicial'].sum(),
        'fuera_rango': df_resumen['fuera_rango'].sum(),
        'segmentos_imposibles': df_resumen['segmentos_imposibles'].sum(),
        'puntos_eliminados_velocidad': df_resumen['puntos_eliminados_velocidad'].sum(),
        'puntos_final': df_resumen['puntos_final'].sum(),
        'velocidad_max_detectada': df_resumen['velocidad_max_detectada'].max()
    }
    df_resumen = pd.concat([df_resumen, pd.DataFrame([totales])], ignore_index=True)
    
    # Guardar
    archivo_resumen = os.path.join(directorio_salida, 'Tabla16_filtrado_coherencia_biologica.csv')
    df_resumen.to_csv(archivo_resumen, index=False)
    
    print("\n" + "="*60)
    print(f"✓ Tabla resumen guardada: {archivo_resumen}")
    print(f"✓ {len(archivos)} archivos procesados")
    print("="*60)
    
    return df_resumen
