"""
Módulo: Análisis de Trayectorias
Descripción: Calcula métricas de movimiento y genera visualizaciones
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

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


def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula distancia en km entre dos puntos usando fórmula Haversine.
    """
    R = 6371  # Radio de la Tierra en km
    
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    
    a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c


def analizar_trayectoria(archivo_csv):
    """
    Analiza una trayectoria y calcula métricas de movimiento.
    """
    
    print(f"\nAnalizando: {os.path.basename(archivo_csv)}")
    
    # Leer CSV
    df = pd.read_csv(archivo_csv)
    df.columns = df.columns.str.strip()
    
    # Detectar columnas
    lat_col, lon_col, fecha_col = detectar_columnas(df)
    
    if lat_col is None or lon_col is None:
        print(f"  ❌ No se encontraron columnas de coordenadas")
        return None
    
    # Obtener ID del transmisor
    transmisor_id = os.path.basename(archivo_csv).split('_')[0]
    
    # Ordenar por fecha
    if fecha_col:
        df[fecha_col] = pd.to_datetime(df[fecha_col])
        df = df.sort_values(by=fecha_col).reset_index(drop=True)
    
    # Filtrar datos válidos
    df = df.dropna(subset=[lat_col, lon_col])
    
    if len(df) < 2:
        print(f"  ⚠ Insuficientes puntos ({len(df)})")
        return None
    
    # Calcular distancias entre puntos consecutivos
    distancias = []
    for i in range(len(df) - 1):
        dist = calcular_distancia_haversine(
            df.iloc[i][lat_col], df.iloc[i][lon_col],
            df.iloc[i+1][lat_col], df.iloc[i+1][lon_col]
        )
        distancias.append(dist)
    
    # Métricas básicas
    distancia_total = sum(distancias)  # km
    
    # Distancia neta (inicio a fin)
    distancia_neta = calcular_distancia_haversine(
        df.iloc[0][lat_col], df.iloc[0][lon_col],
        df.iloc[-1][lat_col], df.iloc[-1][lon_col]
    )
    
    # Índice de rectitud (straightness index)
    indice_rectitud = (distancia_neta / distancia_total) if distancia_total > 0 else 0
    
    # Rango espacial
    lat_min, lat_max = df[lat_col].min(), df[lat_col].max()
    lon_min, lon_max = df[lon_col].min(), df[lon_col].max()
    rango_latitudinal = lat_max - lat_min
    rango_longitudinal = lon_max - lon_min
    
    # Velocidades con filtro de velocidades imposibles
    if fecha_col:
        velocidades = []
        velocidades_todas = []  # Para contar eliminadas
        
        for i in range(len(df) - 1):
            delta_tiempo = (df.iloc[i+1][fecha_col] - df.iloc[i][fecha_col]).total_seconds() / 3600  # horas
            if delta_tiempo > 0:
                velocidad = distancias[i] / delta_tiempo  # km/h
                velocidades_todas.append(velocidad)
                
                # FILTRAR velocidades imposibles (tortugas nadan < 10 km/h típicamente)
                # Umbral conservador de 10 km/h basado en literatura
                if velocidad < 10.0:
                    velocidades.append(velocidad)
        
        velocidad_promedio = np.mean(velocidades) if velocidades else 0
        velocidad_maxima = np.max(velocidades) if velocidades else 0
        velocidad_mediana = np.median(velocidades) if velocidades else 0
        
        # Contar velocidades filtradas
        velocidades_filtradas = len(velocidades_todas) - len(velocidades)
        if velocidades_filtradas > 0:
            print(f"  ⚠ {velocidades_filtradas} velocidades imposibles filtradas (> 10 km/h)")
        
        # Duración total
        duracion_dias = (df.iloc[-1][fecha_col] - df.iloc[0][fecha_col]).days
        
        # Fecha inicio y fin
        fecha_inicio = df.iloc[0][fecha_col].strftime('%Y-%m-%d')
        fecha_fin = df.iloc[-1][fecha_col].strftime('%Y-%m-%d')
    else:
        velocidad_promedio = 0
        velocidad_maxima = 0
        velocidad_mediana = 0
        duracion_dias = 0
        fecha_inicio = 'N/A'
        fecha_fin = 'N/A'
    
    # Área explorada (bounding box aproximado en km²)
    area_aproximada = rango_latitudinal * rango_longitudinal * 111 * 111  # km²
    
    # Distancia promedio por día
    distancia_por_dia = (distancia_total / duracion_dias) if duracion_dias > 0 else 0
    
    estadisticas = {
        'transmisor_id': transmisor_id,
        'num_puntos': len(df),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'duracion_dias': duracion_dias,
        'distancia_total_km': round(distancia_total, 1),
        'distancia_neta_km': round(distancia_neta, 1),
        'distancia_por_dia_km': round(distancia_por_dia, 1),
        'indice_rectitud': round(indice_rectitud, 3),
        'velocidad_promedio_kmh': round(velocidad_promedio, 2),
        'velocidad_mediana_kmh': round(velocidad_mediana, 2),
        'velocidad_maxima_kmh': round(velocidad_maxima, 2),
        'rango_lat_grados': round(rango_latitudinal, 3),
        'rango_lon_grados': round(rango_longitudinal, 3),
        'area_aproximada_km2': round(area_aproximada, 1)
    }
    
    print(f"  Puntos: {len(df)}")
    print(f"  Duración: {duracion_dias} días")
    print(f"  Distancia total: {distancia_total:.1f} km")
    print(f"  Distancia neta: {distancia_neta:.1f} km")
    print(f"  Velocidad promedio: {velocidad_promedio:.2f} km/h")
    print(f"  Índice rectitud: {indice_rectitud:.3f}")
    
    return estadisticas


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
    print("="*60)
    
    todas_estadisticas = []
    
    for archivo in archivos:
        ruta_archivo = os.path.join(directorio_entrada, archivo)
        stats = analizar_trayectoria(ruta_archivo)
        
        if stats is None:
            print(f"  ⚠ Saltando archivo por error")
            continue
        
        todas_estadisticas.append(stats)
    
    if not todas_estadisticas:
        print("\n❌ No se procesaron archivos exitosamente")
        return None
    
    # Crear tabla resumen
    df_resumen = pd.DataFrame(todas_estadisticas)
    
    # Ordenar por transmisor_id
    df_resumen = df_resumen.sort_values('transmisor_id').reset_index(drop=True)
    
    # Guardar
    archivo_resumen = os.path.join(directorio_salida, 'Tabla15_metricas_movimiento.csv')
    df_resumen.to_csv(archivo_resumen, index=False)
    
    print("\n" + "="*60)
    print(f"✓ Tabla resumen guardada: {archivo_resumen}")
    print(f"✓ {len(archivos)} archivos procesados")
    print("="*60)
    
    return df_resumen