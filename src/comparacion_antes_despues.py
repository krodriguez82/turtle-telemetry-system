"""
Módulo: Comparación Antes/Después del Procesamiento
Descripción: Genera mapas comparativos de datos crudos vs procesados
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import folium
import os

def detectar_columnas(df):
    """Detecta columnas de coordenadas"""
    lat_col = lon_col = None
    
    for col in df.columns:
        if 'lat' in col.lower():
            lat_col = col
        if 'lon' in col.lower() or 'long' in col.lower():
            lon_col = col
    
    return lat_col, lon_col


def generar_mapa_comparativo(archivo_crudo, archivo_procesado, directorio_salida, transmisor_id):
    """
    Genera mapa comparativo lado a lado: datos crudos vs procesados.
    """
    
    print(f"\nGenerando comparación para transmisor {transmisor_id}...")
    
    # Leer datos crudos
    df_crudo = pd.read_csv(archivo_crudo)
    df_crudo.columns = df_crudo.columns.str.strip()
    
    # Leer datos procesados
    df_procesado = pd.read_csv(archivo_procesado)
    df_procesado.columns = df_procesado.columns.str.strip()
    
    # Detectar columnas
    lat_col_crudo, lon_col_crudo = detectar_columnas(df_crudo)
    lat_col_proc, lon_col_proc = detectar_columnas(df_procesado)
    
    if not all([lat_col_crudo, lon_col_crudo, lat_col_proc, lon_col_proc]):
        print(f"  ❌ Error detectando columnas")
        return None
    
    # Filtrar coordenadas válidas
    df_crudo_valido = df_crudo.dropna(subset=[lat_col_crudo, lon_col_crudo])
    df_proc_valido = df_procesado.dropna(subset=[lat_col_proc, lon_col_proc])
    
    # Calcular centro
    lat_center = df_proc_valido[lat_col_proc].mean()
    lon_center = df_proc_valido[lon_col_proc].mean()
    
    # Crear mapa
    m = folium.Map(
        location=[lat_center, lon_center],
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # CAPA 1: Datos CRUDOS (rojo/rosa - todos los puntos)
    print(f"  Añadiendo {len(df_crudo_valido)} puntos crudos...")
    for idx, row in df_crudo_valido.iterrows():
        folium.CircleMarker(
            location=[row[lat_col_crudo], row[lon_col_crudo]],
            radius=3,
            popup=f"<b>CRUDO</b><br>Lat: {row[lat_col_crudo]:.4f}<br>Lon: {row[lon_col_crudo]:.4f}",
            tooltip="Dato crudo (sin procesar)",
            color='red',
            fill=True,
            fillColor='pink',
            fillOpacity=0.4,
            weight=1
        ).add_to(m)
    
    # CAPA 2: Datos PROCESADOS (azul/verde - solo los que pasaron filtros)
    print(f"  Añadiendo {len(df_proc_valido)} puntos procesados...")
    coords_procesados = []
    for idx, row in df_proc_valido.iterrows():
        coords_procesados.append([row[lat_col_proc], row[lon_col_proc]])
        
        folium.CircleMarker(
            location=[row[lat_col_proc], row[lon_col_proc]],
            radius=4,
            popup=f"<b>PROCESADO</b><br>Lat: {row[lat_col_proc]:.4f}<br>Lon: {row[lon_col_proc]:.4f}",
            tooltip="Dato procesado (alta calidad)",
            color='darkblue',
            fill=True,
            fillColor='lightblue',
            fillOpacity=0.8,
            weight=2
        ).add_to(m)
    
    # Añadir línea de trayectoria procesada
    folium.PolyLine(
        coords_procesados,
        color='blue',
        weight=2,
        opacity=0.7,
        popup="Trayectoria procesada"
    ).add_to(m)
    
    # Calcular estadísticas
    puntos_eliminados = len(df_crudo_valido) - len(df_proc_valido)
    porcentaje_retenido = (len(df_proc_valido) / len(df_crudo_valido) * 100) if len(df_crudo_valido) > 0 else 0
    
    # Leyenda
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 280px; 
                background-color: white; border:3px solid grey; z-index:9999; 
                font-size:12px; padding: 15px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    <p style="margin:0 0 10px 0; font-size:14px;"><b>🔍 COMPARACIÓN: ANTES vs DESPUÉS</b></p>
    <hr style="margin:8px 0;">
    <p style="margin:5px 0;"><b>Transmisor:</b> {transmisor_id}</p>
    <hr style="margin:8px 0;">
    <p style="margin:5px 0;"><span style="color:red; font-size:16px;">⬤</span> <b>DATOS CRUDOS</b></p>
    <p style="margin:2px 0 2px 20px; font-size:11px;">Total: {len(df_crudo_valido)} puntos</p>
    <p style="margin:2px 0 5px 20px; font-size:11px; color:#666;">Incluye errores y baja calidad</p>
    
    <p style="margin:5px 0;"><span style="color:blue; font-size:16px;">⬤</span> <b>DATOS PROCESADOS</b></p>
    <p style="margin:2px 0 2px 20px; font-size:11px;">Total: {len(df_proc_valido)} puntos</p>
    <p style="margin:2px 0 5px 20px; font-size:11px; color:#666;">Alta calidad (LC1-LC3)</p>
    
    <hr style="margin:8px 0;">
    <p style="margin:5px 0;"><b>📊 Resumen:</b></p>
    <p style="margin:2px 0 2px 20px; font-size:11px;">Eliminados: {puntos_eliminados} ({100-porcentaje_retenido:.1f}%)</p>
    <p style="margin:2px 0 2px 20px; font-size:11px;">Retenidos: {len(df_proc_valido)} ({porcentaje_retenido:.1f}%)</p>
    
    <hr style="margin:8px 0;">
    <p style="margin:0; font-size:10px; color:#666;"><i>El procesamiento eliminó puntos con errores grandes, en tierra, y baja calidad Argos</i></p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Guardar
    nombre_archivo = os.path.join(directorio_salida, f'comparacion_{transmisor_id}_crudo_vs_procesado.html')
    m.save(nombre_archivo)
    
    print(f"  ✓ Mapa comparativo guardado: {nombre_archivo}")
    print(f"  📊 Crudos: {len(df_crudo_valido)} | Procesados: {len(df_proc_valido)} | Retenidos: {porcentaje_retenido:.1f}%")
    
    return {
        'transmisor': transmisor_id,
        'puntos_crudos': len(df_crudo_valido),
        'puntos_procesados': len(df_proc_valido),
        'porcentaje_retenido': round(porcentaje_retenido, 1)
    }


def procesar_comparaciones(directorio_raw, directorio_procesado, directorio_salida, transmisores=None):
    """
    Genera mapas comparativos para múltiples transmisores.
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Si no se especifican transmisores, usar todos
    if transmisores is None:
        archivos_procesados = [f for f in os.listdir(directorio_procesado) 
                               if f.endswith('_simplificado_DP.csv')]
        transmisores = [f.split('_')[0] for f in archivos_procesados]
    
    print(f"Generando comparaciones para {len(transmisores)} transmisores")
    print("="*60)
    
    resultados = []
    
    for trans_id in transmisores:
        # Buscar archivo crudo (ACTUALIZADO para incluir -Argos)
        archivo_crudo = os.path.join(directorio_raw, f"{trans_id}-Argos.csv")
        
        # Buscar archivo procesado
        archivo_procesado = os.path.join(directorio_procesado, f"{trans_id}_simplificado_DP.csv")
        
        if not os.path.exists(archivo_crudo):
            print(f"\n⚠ No se encontró archivo crudo: {archivo_crudo}")
            continue
        
        if not os.path.exists(archivo_procesado):
            print(f"\n⚠ No se encontró archivo procesado: {archivo_procesado}")
            continue
        
        # Generar comparación
        resultado = generar_mapa_comparativo(archivo_crudo, archivo_procesado, 
                                            directorio_salida, trans_id)
        
        if resultado:
            resultados.append(resultado)
    
    # Guardar resumen
    if resultados:
        df_resumen = pd.DataFrame(resultados)
        archivo_resumen = os.path.join(directorio_salida, 'resumen_comparaciones.csv')
        df_resumen.to_csv(archivo_resumen, index=False)
        
        print("\n" + "="*60)
        print("RESUMEN DE COMPARACIONES")
        print("="*60)
        print(df_resumen.to_string(index=False))
        print("="*60)
        print(f"\n✓ Resumen guardado: {archivo_resumen}")
    
    print(f"\n✓ {len(resultados)} mapas comparativos generados en: {directorio_salida}")
    
    return resultados