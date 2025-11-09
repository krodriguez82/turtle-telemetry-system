"""
Módulo: Visualización de Trayectorias
Descripción: Genera mapas HTML interactivos con Folium
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import numpy as np
import folium
import geopy.distance
import os

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


def generar_mapa_trayectoria(archivo_csv, directorio_salida):
    """
    Genera un mapa HTML interactivo de la trayectoria con puntos clickeables.
    """
    
    print(f"\nGenerando mapa: {os.path.basename(archivo_csv)}")
    
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
    
    # Ordenar por fecha si existe
    if fecha_col:
        df[fecha_col] = pd.to_datetime(df[fecha_col])
        df = df.sort_values(by=fecha_col).reset_index(drop=True)
    
    # Eliminar valores NaN
    df = df.dropna(subset=[lat_col, lon_col])
    
    if len(df) < 2:
        print(f"  ⚠ Insuficientes puntos ({len(df)})")
        return None
    
    print(f"  Puntos en trayectoria: {len(df)}")
    
    # Agregar columnas para velocidad y distancia
    df['Speed'] = 0.0
    df['Distance'] = 0.0
    
    for i in range(1, len(df)):
        coord1 = (df.iloc[i-1][lat_col], df.iloc[i-1][lon_col])
        coord2 = (df.iloc[i][lat_col], df.iloc[i][lon_col])
        
        # Calcular distancia en km
        distance = geopy.distance.distance(coord1, coord2).km
        df.loc[i, 'Distance'] = distance
        
        # Calcular velocidad si hay columna de fecha
        if fecha_col:
            time_hours = (df.iloc[i][fecha_col] - df.iloc[i-1][fecha_col]).total_seconds() / 3600
            if time_hours > 0:
                df.loc[i, 'Speed'] = distance / time_hours
            else:
                df.loc[i, 'Speed'] = np.nan
        else:
            df.loc[i, 'Speed'] = np.nan
    
    # Calcular centro del mapa
    lat_center = df[lat_col].mean()
    lon_center = df[lon_col].mean()
    
    # Crear mapa
    m = folium.Map(
        location=[lat_center, lon_center], 
        zoom_start=9,
        tiles='OpenStreetMap'
    )
    
    # Añadir marcador de inicio (verde)
    folium.Marker(
        [df.iloc[0][lat_col], df.iloc[0][lon_col]], 
        popup=f"""
        <b>🟢 INICIO</b><br>
        <b>Transmisor:</b> {transmisor_id}<br>
        <b>Fecha:</b> {df.iloc[0][fecha_col].strftime('%Y-%m-%d %H:%M') if fecha_col else 'N/A'}<br>
        <b>Latitud:</b> {df.iloc[0][lat_col]:.4f}<br>
        <b>Longitud:</b> {df.iloc[0][lon_col]:.4f}
        """,
        tooltip=f"Inicio - {transmisor_id}",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    
    # Añadir marcador de fin (rojo)
    folium.Marker(
        [df.iloc[-1][lat_col], df.iloc[-1][lon_col]], 
        popup=f"""
        <b>🔴 FIN</b><br>
        <b>Transmisor:</b> {transmisor_id}<br>
        <b>Fecha:</b> {df.iloc[-1][fecha_col].strftime('%Y-%m-%d %H:%M') if fecha_col else 'N/A'}<br>
        <b>Latitud:</b> {df.iloc[-1][lat_col]:.4f}<br>
        <b>Longitud:</b> {df.iloc[-1][lon_col]:.4f}<br>
        <b>Distancia total:</b> {df['Distance'].sum():.2f} km
        """,
        tooltip=f"Fin - {transmisor_id}",
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(m)
    
    # Añadir la ruta con información de velocidad y distancia
    for i in range(1, len(df)):
        coords = [
            [df.iloc[i-1][lat_col], df.iloc[i-1][lon_col]], 
            [df.iloc[i][lat_col], df.iloc[i][lon_col]]
        ]
        speed = df.iloc[i]['Speed']
        distance = df.iloc[i]['Distance']
        
        if np.isfinite(speed):
            popup_text = f"""
            <b>Segmento {i}</b><br>
            <b>Velocidad:</b> {speed:.2f} km/h<br>
            <b>Distancia:</b> {distance:.2f} km<br>
            <b>Fecha:</b> {df.iloc[i][fecha_col].strftime('%Y-%m-%d %H:%M') if fecha_col else 'N/A'}
            """
        else:
            popup_text = f"""
            <b>Segmento {i}</b><br>
            <b>Velocidad:</b> N/A<br>
            <b>Distancia:</b> {distance:.2f} km<br>
            <b>Fecha:</b> {df.iloc[i][fecha_col].strftime('%Y-%m-%d %H:%M') if fecha_col else 'N/A'}
            """
        
        # Color según velocidad
        if np.isfinite(speed):
            if speed < 1:
                color = 'blue'  # Lento
            elif speed < 3:
                color = 'green'  # Moderado
            elif speed < 5:
                color = 'orange'  # Rápido
            else:
                color = 'red'  # Muy rápido (posible error)
        else:
            color = 'gray'
        
        folium.PolyLine(
            coords, 
            color=color, 
            weight=2.5, 
            opacity=0.7, 
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(m)
    
    # NUEVO: Añadir TODOS los puntos como marcadores clickeables
    for i in range(len(df)):
        # Determinar color del marcador según velocidad
        speed = df.iloc[i]['Speed']
        if np.isfinite(speed):
            if speed < 1:
                marker_color = 'lightblue'
            elif speed < 3:
                marker_color = 'lightgreen'
            elif speed < 5:
                marker_color = 'orange'
            else:
                marker_color = 'pink'
        else:
            marker_color = 'lightgray'
        
        # Información completa del punto
        if i == 0:
            punto_tipo = "🟢 Inicio"
        elif i == len(df) - 1:
            punto_tipo = "🔴 Fin"
        else:
            punto_tipo = f"📍 Punto {i}"
        
        popup_info = f"""
        <div style="font-family: Arial; font-size: 12px;">
        <b>{punto_tipo}</b><br>
        <b>Transmisor:</b> {transmisor_id}<br>
        <b>Fecha:</b> {df.iloc[i][fecha_col].strftime('%Y-%m-%d %H:%M:%S') if fecha_col else 'N/A'}<br>
        <b>Latitud:</b> {df.iloc[i][lat_col]:.6f}°<br>
        <b>Longitud:</b> {df.iloc[i][lon_col]:.6f}°<br>
        <b>Velocidad:</b> {df.iloc[i]['Speed']:.2f} km/h<br>
        <b>Distancia desde anterior:</b> {df.iloc[i]['Distance']:.2f} km
        </div>
        """
        
        tooltip_info = f"Punto {i}: {df.iloc[i][fecha_col].strftime('%Y-%m-%d %H:%M') if fecha_col else 'N/A'}"
        
        # Evitar duplicar marcadores de inicio y fin
        if i != 0 and i != len(df) - 1:
            folium.CircleMarker(
                location=[df.iloc[i][lat_col], df.iloc[i][lon_col]],
                radius=4,
                popup=folium.Popup(popup_info, max_width=300),
                tooltip=tooltip_info,
                color='darkblue',
                fill=True,
                fillColor=marker_color,
                fillOpacity=0.8,
                weight=1
            ).add_to(m)
    
    # Agregar leyenda
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 220px; height: 180px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px">
    <p style="margin:0; padding:0;"><b>Transmisor: ''' + transmisor_id + '''</b></p>
    <p style="margin:0; padding:0;"><b>Total puntos: ''' + str(len(df)) + '''</b></p>
    <hr style="margin:5px 0;">
    <p style="margin:0; padding:0;"><b>Velocidad:</b></p>
    <p style="margin:2px 0;"><span style="color:blue;">━━━</span> < 1 km/h</p>
    <p style="margin:2px 0;"><span style="color:green;">━━━</span> 1-3 km/h</p>
    <p style="margin:2px 0;"><span style="color:orange;">━━━</span> 3-5 km/h</p>
    <p style="margin:2px 0;"><span style="color:red;">━━━</span> > 5 km/h</p>
    <hr style="margin:5px 0;">
    <p style="margin:0; padding:0; font-size:10px;"><i>Haz clic en los puntos para más info</i></p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Guardar mapa
    nombre_mapa = os.path.join(directorio_salida, f'mapa_{transmisor_id}.html')
    m.save(nombre_mapa)
    print(f"  ✓ Mapa guardado: {nombre_mapa}")
    
    return nombre_mapa


def generar_mapa_consolidado(directorio_entrada, directorio_salida):
    """
    Genera un mapa con todas las trayectorias juntas.
    """
    
    print("\n" + "="*60)
    print("Generando mapa consolidado de todas las trayectorias...")
    print("="*60)
    
    # Buscar archivos
    archivos = [f for f in os.listdir(directorio_entrada) 
                if f.endswith('_simplificado_DP.csv')]
    
    if not archivos:
        print(f"❌ No se encontraron archivos")
        return None
    
    # Colores para cada tortuga
    colores = ['blue', 'green', 'red', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen']
    
    # Crear mapa centrado en Panamá
    m = folium.Map(
        location=[8.0, -80.0], 
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    leyenda_items = []
    
    for idx, archivo in enumerate(archivos):
        ruta_archivo = os.path.join(directorio_entrada, archivo)
        df = pd.read_csv(ruta_archivo)
        df.columns = df.columns.str.strip()
        
        lat_col, lon_col, fecha_col = detectar_columnas(df)
        
        if lat_col is None or lon_col is None:
            continue
        
        transmisor_id = os.path.basename(archivo).split('_')[0]
        color = colores[idx % len(colores)]
        
        # Ordenar y limpiar
        if fecha_col:
            df[fecha_col] = pd.to_datetime(df[fecha_col])
            df = df.sort_values(by=fecha_col).reset_index(drop=True)
        
        df = df.dropna(subset=[lat_col, lon_col])
        
        if len(df) < 2:
            continue
        
        # Marcador inicio
        folium.CircleMarker(
            [df.iloc[0][lat_col], df.iloc[0][lon_col]],
            radius=6,
            popup=f"""<b>Inicio {transmisor_id}</b><br>
                      Fecha: {df.iloc[0][fecha_col].strftime('%Y-%m-%d') if fecha_col else 'N/A'}<br>
                      Puntos totales: {len(df)}""",
            tooltip=f"Inicio {transmisor_id}",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.9
        ).add_to(m)
        
        # Trayectoria
        coords = [[row[lat_col], row[lon_col]] for _, row in df.iterrows()]
        folium.PolyLine(
            coords,
            color=color,
            weight=2.5,
            opacity=0.7,
            popup=f"Transmisor {transmisor_id} ({len(df)} puntos)",
            tooltip=f"Transmisor {transmisor_id}"
        ).add_to(m)
        
        leyenda_items.append(f'<p style="margin:2px 0;"><span style="color:{color};">━━━</span> {transmisor_id} ({len(df)} pts)</p>')
    
    # Agregar leyenda
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 220px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px; max-height: 450px; overflow-y: auto;">
    <p style="margin:0 0 5px 0;"><b>🐢 Transmisores:</b></p>
    ''' + ''.join(leyenda_items) + '''
    <hr style="margin:5px 0;">
    <p style="margin:0; font-size:10px;"><i>Haz clic en las líneas para más info</i></p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Guardar
    nombre_mapa = os.path.join(directorio_salida, 'mapa_consolidado_todas_trayectorias.html')
    m.save(nombre_mapa)
    print(f"✓ Mapa consolidado guardado: {nombre_mapa}")
    
    return nombre_mapa


def procesar_visualizaciones(directorio_entrada, directorio_salida):
    """
    Genera todos los mapas HTML.
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Buscar archivos
    archivos = [f for f in os.listdir(directorio_entrada) 
                if f.endswith('_simplificado_DP.csv')]
    
    if not archivos:
        print(f"\n❌ No se encontraron archivos en: {directorio_entrada}")
        return
    
    print(f"Archivos a procesar: {len(archivos)}")
    print("="*60)
    
    # Generar mapa individual para cada tortuga
    for archivo in archivos:
        ruta_archivo = os.path.join(directorio_entrada, archivo)
        generar_mapa_trayectoria(ruta_archivo, directorio_salida)
    
    # Generar mapa consolidado
    generar_mapa_consolidado(directorio_entrada, directorio_salida)
    
    print("\n" + "="*60)
    print(f"✓ Todos los mapas generados en: {directorio_salida}")
    print("="*60)