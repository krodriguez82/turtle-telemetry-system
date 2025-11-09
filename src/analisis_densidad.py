"""
Módulo: Análisis de Densidad Espacial
Descripción: Genera mapas de densidad Kernel (KDE) y análisis de hotspots
Autor: [Tu nombre]
Proyecto: Procesamiento de Datos de Tortugas Marinas - SENACYT
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde
import folium
from folium.plugins import HeatMap
import os

def detectar_columnas(df):
    """Detecta columnas necesarias"""
    lat_col = lon_col = None
    
    for col in df.columns:
        if 'lat' in col.lower():
            lat_col = col
        if 'lon' in col.lower() or 'long' in col.lower():
            lon_col = col
    
    return lat_col, lon_col


def cargar_todos_datos(directorio_entrada):
    """
    Carga todos los archivos CSV y los consolida en un único DataFrame.
    """
    
    archivos = [f for f in os.listdir(directorio_entrada) 
                if f.endswith('_simplificado_DP')]
    
    if not archivos:
        print(f"❌ No se encontraron archivos")
        return None
    
    todos_datos = []
    
    for archivo in archivos:
        ruta = os.path.join(directorio_entrada, archivo)
        df = pd.read_csv(ruta)
        df.columns = df.columns.str.strip()
        
        transmisor_id = os.path.basename(archivo).split('_')[0]
        df['transmisor'] = transmisor_id
        
        todos_datos.append(df)
    
    df_consolidado = pd.concat(todos_datos, ignore_index=True)
    
    print(f"✓ {len(archivos)} archivos cargados")
    print(f"✓ Total puntos: {len(df_consolidado)}")
    
    return df_consolidado


def generar_mapa_calor(df, directorio_salida):
    """
    Genera mapa de calor (heatmap) usando Folium con puntos coloreados por tortuga.
    """
    
    print("\nGenerando mapa de calor con puntos individuales...")
    
    lat_col, lon_col = detectar_columnas(df)
    
    if lat_col is None or lon_col is None:
        print("❌ No se encontraron columnas de coordenadas")
        return None
    
    # Filtrar datos válidos
    df_valido = df.dropna(subset=[lat_col, lon_col])
    
    # Preparar datos para heatmap
    heat_data = [[row[lat_col], row[lon_col]] for _, row in df_valido.iterrows()]
    
    # Crear mapa centrado en el promedio de coordenadas
    lat_center = df_valido[lat_col].mean()
    lon_center = df_valido[lon_col].mean()
    
    m = folium.Map(
        location=[lat_center, lon_center],
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # Añadir capa de calor
    HeatMap(
        heat_data,
        radius=15,
        blur=25,
        max_zoom=13,
        gradient={
            0.0: 'blue',
            0.4: 'cyan',
            0.6: 'lime',
            0.8: 'yellow',
            1.0: 'red'
        }
    ).add_to(m)
    
    # Colores para cada tortuga
    colores = {
        '241136': 'blue',
        '241137': 'green', 
        '241138': 'red',
        '241139': 'purple',
        '241140': 'orange',
        '241141': 'darkred',
        '241142': 'darkblue',
        '241143': 'darkgreen'
    }
    
    # Añadir puntos individuales coloreados por tortuga
    print("  Añadiendo puntos individuales...")
    transmisores_unicos = df_valido['transmisor'].unique()
    
    for transmisor in transmisores_unicos:
        df_trans = df_valido[df_valido['transmisor'] == transmisor]
        color = colores.get(transmisor, 'gray')
        
        for idx, row in df_trans.iterrows():
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=3,
                popup=f"<b>Transmisor:</b> {transmisor}<br><b>Lat:</b> {row[lat_col]:.4f}<br><b>Lon:</b> {row[lon_col]:.4f}",
                tooltip=f"{transmisor}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=1
            ).add_to(m)
    
    # Construir leyenda con todos los transmisores
    leyenda_items = []
    for transmisor in sorted(transmisores_unicos):
        color = colores.get(transmisor, 'gray')
        puntos = len(df_valido[df_valido['transmisor'] == transmisor])
        leyenda_items.append(f'<p style="margin:2px 0;"><span style="color:{color};">⬤</span> {transmisor} ({puntos} pts)</p>')
    
    # Añadir leyenda
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 220px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:11px; padding: 10px; max-height: 450px; overflow-y: auto;">
    <p style="margin:0 0 5px 0;"><b>🔥 Mapa de Densidad + Puntos</b></p>
    <hr style="margin:5px 0;">
    <p style="margin:2px 0; font-size:10px;"><b>Transmisores:</b></p>
    ''' + ''.join(leyenda_items) + '''
    <hr style="margin:5px 0;">
    <p style="margin:2px 0; font-size:10px;"><b>Densidad:</b></p>
    <p style="margin:2px 0;"><span style="color:red;">⬤</span> Muy Alta</p>
    <p style="margin:2px 0;"><span style="color:yellow;">⬤</span> Alta</p>
    <p style="margin:2px 0;"><span style="color:lime;">⬤</span> Media</p>
    <p style="margin:2px 0;"><span style="color:cyan;">⬤</span> Baja</p>
    <hr style="margin:5px 0;">
    <p style="margin:0; font-size:9px;"><i>Total puntos: ''' + str(len(df_valido)) + '''</i></p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Guardar
    archivo_salida = os.path.join(directorio_salida, 'mapa_densidad_calor_con_puntos.html')
    m.save(archivo_salida)
    print(f"✓ Mapa de calor con puntos guardado: {archivo_salida}")
    
    return archivo_salida


def generar_mapa_puntos_coloreados(df, directorio_salida):
    """
    Genera mapa SOLO con puntos coloreados por tortuga (sin heatmap).
    """
    
    print("\nGenerando mapa de puntos coloreados por tortuga...")
    
    lat_col, lon_col = detectar_columnas(df)
    
    if lat_col is None or lon_col is None:
        print("❌ No se encontraron columnas de coordenadas")
        return None
    
    # Filtrar datos válidos
    df_valido = df.dropna(subset=[lat_col, lon_col])
    
    # Crear mapa
    lat_center = df_valido[lat_col].mean()
    lon_center = df_valido[lon_col].mean()
    
    m = folium.Map(
        location=[lat_center, lon_center],
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # Colores para cada tortuga
    colores = {
        '241136': 'blue',
        '241137': 'green', 
        '241138': 'red',
        '241139': 'purple',
        '241140': 'orange',
        '241141': 'darkred',
        '241142': 'darkblue',
        '241143': 'darkgreen'
    }
    
    # Añadir puntos
    transmisores_unicos = df_valido['transmisor'].unique()
    
    for transmisor in transmisores_unicos:
        df_trans = df_valido[df_valido['transmisor'] == transmisor]
        color = colores.get(transmisor, 'gray')
        
        for idx, row in df_trans.iterrows():
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=4,
                popup=f"<b>Transmisor:</b> {transmisor}<br><b>Lat:</b> {row[lat_col]:.4f}<br><b>Lon:</b> {row[lon_col]:.4f}",
                tooltip=f"{transmisor}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=1
            ).add_to(m)
    
    # Leyenda
    leyenda_items = []
    for transmisor in sorted(transmisores_unicos):
        color = colores.get(transmisor, 'gray')
        puntos = len(df_valido[df_valido['transmisor'] == transmisor])
        leyenda_items.append(f'<p style="margin:2px 0;"><span style="color:{color};">⬤</span> {transmisor} ({puntos} pts)</p>')
    
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 220px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:11px; padding: 10px; max-height: 450px; overflow-y: auto;">
    <p style="margin:0 0 5px 0;"><b>🐢 Puntos por Transmisor</b></p>
    <hr style="margin:5px 0;">
    ''' + ''.join(leyenda_items) + '''
    <hr style="margin:5px 0;">
    <p style="margin:0; font-size:9px;"><i>Total: ''' + str(len(df_valido)) + ''' puntos</i></p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Guardar
    archivo_salida = os.path.join(directorio_salida, 'mapa_puntos_coloreados.html')
    m.save(archivo_salida)
    print(f"✓ Mapa de puntos coloreados guardado: {archivo_salida}")
    
    return archivo_salida


def generar_mapa_kde_matplotlib(df, directorio_salida):
    """
    Genera mapa de densidad Kernel usando matplotlib.
    """
    
    print("\nGenerando mapa KDE (matplotlib)...")
    
    lat_col, lon_col = detectar_columnas(df)
    
    if lat_col is None or lon_col is None:
        print("❌ No se encontraron columnas de coordenadas")
        return None
    
    # Filtrar datos válidos
    df_valido = df.dropna(subset=[lat_col, lon_col])
    
    # Extraer coordenadas
    lats = df_valido[lat_col].values
    lons = df_valido[lon_col].values
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Calcular KDE
    try:
        xy = np.vstack([lons, lats])
        kde = gaussian_kde(xy)
        
        # Crear grilla
        lon_min, lon_max = lons.min(), lons.max()
        lat_min, lat_max = lats.min(), lats.max()
        
        lon_grid = np.linspace(lon_min, lon_max, 100)
        lat_grid = np.linspace(lat_min, lat_max, 100)
        lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)
        
        # Evaluar KDE en grilla
        positions = np.vstack([lon_mesh.ravel(), lat_mesh.ravel()])
        density = kde(positions).reshape(lon_mesh.shape)
        
        # Plotear
        contour = ax.contourf(lon_mesh, lat_mesh, density, levels=15, cmap='YlOrRd', alpha=0.7)
        ax.scatter(lons, lats, c='blue', s=5, alpha=0.3, label='Localizaciones')
        
        # Colorbar
        cbar = plt.colorbar(contour, ax=ax, label='Densidad')
        
        # Etiquetas
        ax.set_xlabel('Longitud (°)', fontsize=12)
        ax.set_ylabel('Latitud (°)', fontsize=12)
        ax.set_title('Densidad Espacial de Uso - Kernel Density Estimation (KDE)', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Guardar
        archivo_salida = os.path.join(directorio_salida, 'mapa_kde_densidad.png')
        plt.tight_layout()
        plt.savefig(archivo_salida, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Mapa KDE guardado: {archivo_salida}")
        return archivo_salida
        
    except Exception as e:
        print(f"❌ Error generando KDE: {e}")
        return None


def identificar_hotspots(df, percentil=75):
    """
    Identifica áreas de alta concentración (hotspots).
    """
    
    print(f"\nIdentificando hotspots (percentil {percentil})...")
    
    lat_col, lon_col = detectar_columnas(df)
    
    if lat_col is None or lon_col is None:
        print("❌ No se encontraron columnas de coordenadas")
        return None, None
    
    # Filtrar datos válidos
    df_valido = df.dropna(subset=[lat_col, lon_col])
    
    # Calcular KDE
    lats = df_valido[lat_col].values
    lons = df_valido[lon_col].values
    
    try:
        xy = np.vstack([lons, lats])
        kde = gaussian_kde(xy)
        
        # Evaluar densidad en cada punto
        densidades = kde(xy)
        
        # Identificar umbral de hotspot
        umbral = np.percentile(densidades, percentil)
        
        # Puntos en hotspots
        hotspots = df_valido[densidades >= umbral].copy()
        hotspots['densidad'] = densidades[densidades >= umbral]
        
        print(f"✓ Hotspots identificados: {len(hotspots)} puntos ({len(hotspots)/len(df_valido)*100:.1f}%)")
        
        # Calcular centro de masa de hotspots
        centro_lat = hotspots[lat_col].mean()
        centro_lon = hotspots[lon_col].mean()
        
        print(f"  Centro de hotspot principal: {centro_lat:.4f}°N, {centro_lon:.4f}°W")
        
        estadisticas = {
            'total_puntos': len(df_valido),
            'puntos_hotspot': len(hotspots),
            'porcentaje_hotspot': round(len(hotspots)/len(df_valido)*100, 1),
            'centro_hotspot_lat': round(centro_lat, 4),
            'centro_hotspot_lon': round(centro_lon, 4),
            'rango_lat_hotspot': round(hotspots[lat_col].max() - hotspots[lat_col].min(), 3),
            'rango_lon_hotspot': round(hotspots[lon_col].max() - hotspots[lon_col].min(), 3)
        }
        
        return hotspots, estadisticas
        
    except Exception as e:
        print(f"❌ Error identificando hotspots: {e}")
        return None, None


def procesar_analisis_densidad(directorio_entrada, directorio_salida):
    """
    Ejecuta análisis completo de densidad espacial.
    """
    
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Cargar datos
    df = cargar_todos_datos(directorio_entrada)
    
    if df is None:
        return None
    
    # Generar mapa de calor interactivo CON PUNTOS
    mapa_calor = generar_mapa_calor(df, directorio_salida)
    
    # Generar mapa SOLO con puntos coloreados
    mapa_puntos = generar_mapa_puntos_coloreados(df, directorio_salida)
    
    # Generar mapa KDE estático
    mapa_kde = generar_mapa_kde_matplotlib(df, directorio_salida)
    
    # Identificar hotspots
    hotspots, stats_hotspots = identificar_hotspots(df, percentil=75)
    
    if stats_hotspots:
        # Guardar estadísticas
        df_stats = pd.DataFrame([stats_hotspots])
        archivo_stats = os.path.join(directorio_salida, 'estadisticas_hotspots.csv')
        df_stats.to_csv(archivo_stats, index=False)
        print(f"\n✓ Estadísticas guardadas: {archivo_stats}")
    
    print("\n" + "="*60)
    print("✓ Análisis de densidad completado")
    print("="*60)
    
    return {
        'mapa_calor': mapa_calor,
        'mapa_puntos': mapa_puntos,
        'mapa_kde': mapa_kde,
        'stats_hotspots': stats_hotspots
    }