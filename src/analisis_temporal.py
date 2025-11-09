"""
Módulo: Análisis y Corrección Temporal
Descripción: Analiza consistencia temporal, elimina duplicados y corrige datos
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import os
from datetime import datetime, timedelta

def detectar_columna_fecha(df):
    """Detecta automáticamente la columna de fecha/timestamp"""
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            return col
    return None


def detectar_columna_calidad(df):
    """Detecta columna de calidad Argos"""
    for col in df.columns:
        if 'quality' in col.lower() or 'class' in col.lower():
            return col
    return None


def analizar_y_corregir_temporal(archivo_csv, directorio_salida):
    """
    Analiza y corrige aspectos temporales de los datos.
    Elimina duplicados temporales y reordena cronológicamente.
    """
    
    print(f"\nProcesando: {os.path.basename(archivo_csv)}")
    
    # Leer CSV
    df = pd.read_csv(archivo_csv)
    df.columns = df.columns.str.strip()
    
    # Detectar columnas
    fecha_col = detectar_columna_fecha(df)
    calidad_col = detectar_columna_calidad(df)
    
    if fecha_col is None:
        print(f"  ❌ No se encontró columna de fecha")
        return None, None
    
    print(f"  Columna fecha: {fecha_col}")
    if calidad_col:
        print(f"  Columna calidad: {calidad_col}")
    
    # Convertir a datetime
    try:
        df[fecha_col] = pd.to_datetime(df[fecha_col])
    except Exception as e:
        print(f"  ❌ Error convirtiendo fechas: {e}")
        return None, None
    
    # Obtener ID del transmisor
    transmisor_id = os.path.basename(archivo_csv).split('_')[0]
    total_original = len(df)
    
    # Verificar si está ordenado originalmente
    ordenado_original = df[fecha_col].is_monotonic_increasing
    
    # PASO 1: Ordenar por fecha
    df = df.sort_values(by=fecha_col).reset_index(drop=True)
    
    # PASO 2: Crear columna de fecha al minuto para detectar duplicados
    df['fecha_minuto'] = df[fecha_col].dt.floor('min')
    
    # Contar duplicados ANTES de eliminar
    duplicados_antes = df.duplicated(subset='fecha_minuto', keep=False).sum()
    
    # PASO 3: Eliminar duplicados
    # Si hay columna de calidad, quedarse con el de mejor calidad
    if calidad_col:
        # Mapeo de calidades (LC3 es mejor que LC2, LC2 mejor que LC1)
        calidad_rank = {'LC3': 3, 'LC2': 2, 'LC1': 1, 'LC0': 0, 'A': 0, 'B': 0, 'Z': 0}
        df['calidad_rank'] = df[calidad_col].map(calidad_rank).fillna(0)
        
        # Ordenar por fecha_minuto y calidad (descendente) antes de eliminar duplicados
        df = df.sort_values(['fecha_minuto', 'calidad_rank'], ascending=[True, False])
        df = df.drop_duplicates(subset='fecha_minuto', keep='first')
        
        # Eliminar columna auxiliar
        df = df.drop(columns=['calidad_rank'])
    else:
        # Si no hay columna de calidad, quedarse con el primero
        df = df.drop_duplicates(subset='fecha_minuto', keep='first')
    
    # Eliminar columna auxiliar de fecha_minuto
    df = df.drop(columns=['fecha_minuto'])
    
    # Re-ordenar por fecha después de eliminar duplicados
    df = df.sort_values(by=fecha_col).reset_index(drop=True)
    
    total_despues = len(df)
    duplicados_eliminados = total_original - total_despues
    
    # PASO 4: Detectar intervalos imposiblemente cortos (< 30 segundos)
    df['diff_segundos'] = df[fecha_col].diff().dt.total_seconds()
    intervalos_cortos = ((df['diff_segundos'] > 0) & (df['diff_segundos'] < 30)).sum()
    
    # PASO 5: Calcular intervalos entre transmisiones
    intervalos = df['diff_segundos'] / 3600  # Convertir a horas
    intervalos_validos = intervalos[intervalos > 0]
    
    if len(intervalos_validos) > 0:
        intervalo_promedio = intervalos_validos.mean()
        intervalo_mediano = intervalos_validos.median()
    else:
        intervalo_promedio = 0
        intervalo_mediano = 0
    
    # PASO 6: Detectar gaps significativos (> 72 horas = 3 días)
    gaps_grandes = df[df['diff_segundos'] > 72*3600]
    num_gaps = len(gaps_grandes)
    
    if num_gaps > 0:
        gap_max = gaps_grandes['diff_segundos'].max() / (24*3600)  # días
    else:
        gap_max = 0
    
    # Eliminar columna auxiliar
    df = df.drop(columns=['diff_segundos'])
    
    # PASO 7: Guardar archivo corregido
    nombre_salida = os.path.join(directorio_salida, f"{transmisor_id}_corregido_temporal.csv")
    df.to_csv(nombre_salida, index=False)
    
    estadisticas = {
        'transmisor_id': transmisor_id,
        'puntos_original': total_original,
        'puntos_corregido': total_despues,
        'duplicados_eliminados': duplicados_eliminados,
        'ordenado_original': 'Sí' if ordenado_original else 'No',
        'intervalos_cortos': intervalos_cortos,
        'intervalo_promedio_h': round(intervalo_promedio, 1) if intervalo_promedio > 0 else 0,
        'intervalo_mediano_h': round(intervalo_mediano, 1) if intervalo_mediano > 0 else 0,
        'num_gaps_72h': num_gaps,
        'gap_maximo_dias': round(gap_max, 1) if num_gaps > 0 else 0
    }
    
    print(f"  Original: {total_original} puntos")
    print(f"  Corregido: {total_despues} puntos")
    print(f"  Duplicados eliminados: {duplicados_eliminados}")
    print(f"  Ordenado original: {estadisticas['ordenado_original']}")
    print(f"  Intervalos < 30s: {intervalos_cortos}")
    print(f"  Gaps > 72h: {num_gaps}")
    print(f"  ✓ Guardado: {nombre_salida}")
    
    return df, estadisticas


def procesar_multiples_archivos(directorio_espacial, directorio_salida):
    """
    Procesa múltiples archivos y genera tabla resumen.
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Buscar archivos filtrados espacialmente
    archivos = [f for f in os.listdir(directorio_espacial) 
                if f.endswith('_filtrado_espacial.csv')]
    
    if not archivos:
        print(f"\n❌ No se encontraron archivos en: {directorio_espacial}")
        return None
    
    print(f"Archivos a procesar: {len(archivos)}")
    print("="*60)
    
    todas_estadisticas = []
    
    for archivo in archivos:
        ruta_archivo = os.path.join(directorio_espacial, archivo)
        df_corregido, stats = analizar_y_corregir_temporal(ruta_archivo, directorio_salida)
        
        if stats is None:
            print(f"  ⚠ Saltando archivo por error")
            continue
        
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
        'puntos_corregido': df_resumen['puntos_corregido'].sum(),
        'duplicados_eliminados': df_resumen['duplicados_eliminados'].sum(),
        'ordenado_original': '-',
        'intervalos_cortos': df_resumen['intervalos_cortos'].sum(),
        'intervalo_promedio_h': round(df_resumen['intervalo_promedio_h'].mean(), 1),
        'intervalo_mediano_h': round(df_resumen['intervalo_mediano_h'].median(), 1),
        'num_gaps_72h': df_resumen['num_gaps_72h'].sum(),
        'gap_maximo_dias': '-'
    }
    df_resumen = pd.concat([df_resumen, pd.DataFrame([totales])], ignore_index=True)
    
    # Guardar
    archivo_resumen = os.path.join(directorio_salida, 'Tabla16_correccion_temporal.csv')
    df_resumen.to_csv(archivo_resumen, index=False)
    
    print("\n" + "="*60)
    print(f"✓ Tabla resumen guardada: {archivo_resumen}")
    print(f"✓ {len(archivos)} archivos procesados")
    print("="*60)
    
    return df_resumen