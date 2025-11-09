"""
Módulo: Filtrado por Calidad Argos
Descripción: Filtra datos de telemetría conservando solo LC3, LC2, LC1
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import os

def filtrar_por_calidad_argos(archivo_csv, calidades_aceptadas=['3', '2', '1']):
    """
    Filtra un archivo CSV de Argos conservando solo calidades específicas.
    
    Parámetros:
    - archivo_csv: ruta al archivo CSV
    - calidades_aceptadas: lista de calidades a conservar
    
    Retorna:
    - df_filtrado: DataFrame con datos filtrados
    - estadisticas: diccionario con estadísticas del filtrado
    """
    
    print(f"Procesando: {os.path.basename(archivo_csv)}")
    df = pd.read_csv(archivo_csv)
    df.columns = df.columns.str.strip()
    
    transmisor_id = os.path.basename(archivo_csv).split('-')[0]
    total_original = len(df)
    
    # Contar por clase de calidad
    conteo_original = {}
    for clase in ['3', '2', '1', '0', 'A', 'B', 'Z']:
        conteo_original[f'LC{clase}'] = len(df[df['LocationQuality'] == clase])
    
    # Filtrar
    df_filtrado = df[df['LocationQuality'].isin(calidades_aceptadas)].copy()
    total_retenido = len(df_filtrado)
    porcentaje_retencion = (total_retenido / total_original * 100) if total_original > 0 else 0
    
    estadisticas = {
        'transmisor_id': transmisor_id,
        'total_original': total_original,
        'LC3': conteo_original.get('LC3', 0),
        'LC2': conteo_original.get('LC2', 0),
        'LC1': conteo_original.get('LC1', 0),
        'LC0': conteo_original.get('LC0', 0),
        'LCA': conteo_original.get('LCA', 0),
        'LCB': conteo_original.get('LCB', 0),
        'LCZ': conteo_original.get('LCZ', 0),
        'total_retenido': total_retenido,
        'porcentaje_retencion': round(porcentaje_retencion, 1)
    }
    
    print(f"  Retenido: {total_retenido}/{total_original} ({porcentaje_retencion:.1f}%)")
    
    return df_filtrado, estadisticas


def procesar_multiples_archivos(lista_archivos, directorio_salida):
    """
    Procesa múltiples archivos CSV y genera tabla resumen.
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    todas_estadisticas = []
    
    for archivo in lista_archivos:
        df_filtrado, stats = filtrar_por_calidad_argos(archivo)
        
        nombre_salida = os.path.join(
            directorio_salida, 
            f"{stats['transmisor_id']}_filtrado_calidad.csv"
        )
        df_filtrado.to_csv(nombre_salida, index=False)
        todas_estadisticas.append(stats)
    
    # Crear tabla resumen
    df_resumen = pd.DataFrame(todas_estadisticas)
    columnas_ordenadas = [
        'transmisor_id', 'LC3', 'LC2', 'LC1', 'LC0', 'LCA', 'LCB', 'LCZ',
        'total_original', 'total_retenido', 'porcentaje_retencion'
    ]
    df_resumen = df_resumen[columnas_ordenadas]
    
    # Totales
    totales = {
        'transmisor_id': 'TOTAL',
        'LC3': df_resumen['LC3'].sum(),
        'LC2': df_resumen['LC2'].sum(),
        'LC1': df_resumen['LC1'].sum(),
        'LC0': df_resumen['LC0'].sum(),
        'LCA': df_resumen['LCA'].sum(),
        'LCB': df_resumen['LCB'].sum(),
        'LCZ': df_resumen['LCZ'].sum(),
        'total_original': df_resumen['total_original'].sum(),
        'total_retenido': df_resumen['total_retenido'].sum(),
        'porcentaje_retencion': round(
            df_resumen['total_retenido'].sum() / df_resumen['total_original'].sum() * 100, 1
        )
    }
    df_resumen = pd.concat([df_resumen, pd.DataFrame([totales])], ignore_index=True)
    
    archivo_resumen = os.path.join(directorio_salida, 'Tabla10_resumen_filtrado_calidad.csv')
    df_resumen.to_csv(archivo_resumen, index=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Tabla resumen guardada: {archivo_resumen}")
    print(f"✓ {len(lista_archivos)} archivos procesados")
    print(f"{'='*60}\n")
    
    return df_resumen