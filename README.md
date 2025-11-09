# 🐢 Sistema de Procesamiento de Telemetría Satelital de Tortugas Marinas

Sistema de procesamiento y visualización de datos de telemetría satelital para el monitoreo y seguimiento de tortugas marinas en las costas del Pacífico de Panamá.

## 📋 Descripción

Este proyecto forma parte de la tesis de Maestría en Ingeniería de Software de la Universidad Tecnológica de Panamá. El sistema procesa datos de transmisores SPOT-375B del sistema Argos, aplicando técnicas avanzadas de filtrado, validación y análisis espacial.

## ✨ Características

- ✅ Filtrado por calidad Argos (LC0-LC3)
- ✅ Validación espacial (exclusión de tierra firme)
- ✅ Filtrado por coherencia biológica (velocidades imposibles)
- ✅ Simplificación de trayectorias (Douglas-Peucker)
- ✅ Análisis de métricas de movimiento
- ✅ Visualización interactiva con mapas HTML (Folium)
- ✅ Análisis de densidad espacial (KDE)
- ✅ Comparación antes/después del procesamiento

## 🚀 Instalación

### Requisitos

- Python 3.10+
- pip

### Pasos

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/turtle-telemetry-system.git
cd turtle-telemetry-system
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 📖 Uso

### Procesamiento completo
```python
# 1. Filtrado por calidad Argos
python scripts/ejecutar_filtrado_calidad.py

# 2. Validación espacial
python scripts/ejecutar_filtrado_espacial.py

# 3. Filtrado por velocidad
python scripts/ejecutar_filtrado_coherencia.py

# 4. Simplificación Douglas-Peucker
python scripts/ejecutar_douglas_peucker.py

# 5. Análisis de trayectorias
python scripts/ejecutar_analisis_trayectorias.py

# 6. Análisis de densidad
python scripts/ejecutar_analisis_densidad.py

# 7. Visualización
python scripts/ejecutar_visualizacion_trayectorias.py
```

### Uso de módulos individuales
```python
from src.filtrado_calidad import filtrar_por_clase
from src.visualizacion_trayectorias import generar_mapa_trayectoria

# Filtrar datos
df_filtrado = filtrar_por_clase(df, clases=['LC1', 'LC2', 'LC3'])

# Generar visualización
generar_mapa_trayectoria('datos_procesados.csv', './outputs/')
```

## 📁 Estructura del Proyecto
```
turtle-telemetry-system/
├── src/                    # Módulos de procesamiento
├── scripts/                # Scripts ejecutables
├── data/                   # Datos de ejemplo
├── outputs/                # Resultados generados
├── requirements.txt        # Dependencias
└── README.md              # Este archivo
```

## 🔬 Módulos

### Preprocesamiento
- `filtrado_calidad.py` - Filtrado por clases Argos
- `filtrado_espacial.py` - Validación de coordenadas
- `filtrado_velocidad.py` - Coherencia biológica
- `filtro_area_estudio.py` - Límites geográficos

### Análisis
- `simplificacion_douglas_peucker.py` - Simplificación de trayectorias
- `analisis_trayectorias.py` - Métricas de movimiento
- `analisis_temporal.py` - Análisis temporal
- `analisis_densidad.py` - Densidad espacial (KDE)

### Visualización
- `visualizacion_trayectorias.py` - Mapas interactivos
- `comparacion_antes_despues.py` - Comparaciones visuales

## 📊 Resultados

El sistema genera:
- Archivos CSV procesados
- Mapas HTML interactivos con Folium
- Mapas de densidad de calor
- Métricas de movimiento (distancia, velocidad, rectitud)
- Visualizaciones comparativas

## 🎓 Información Académica

**Autor:** Kexy Rodríguez  
**Asesora:** Dra. Elia Cano  
**Institución:** Universidad Tecnológica de Panamá  
**Programa:** Maestría en Ingeniería de Software  
**Año:** 2025

## 📝 Publicaciones

1. K. Rodríguez-Martínez, C. Rovetto, E. Cano and E. E. Flores, "Optimization of satellite biotelemetry data in sea turtles through outlier removal techniques," 2024 9th International Engineering, Sciences and Technology Conference (IESTEC), Panama City, Panama, 2024, pp. 188-193, doi: 10.1109/IESTEC62784.2024.10820233.

2. C. Rovetto, E. Cruz, E. Flores, I. Nuñez, K. Rodriguez and E. Cano, "Behavioral data analysis of sea turtles from the Pacific coast of Panama, using biotelemetry," 2023 VI Congreso Internacional en Inteligencia Ambiental, Ingeniería de Software y Salud Electrónica y Móvil (AmITIC), Cali, Colombia, 2023, pp. 1-7, doi: 10.1109/AmITIC60194.2023.10366354.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Dr. Eric Flores (datos de telemetría)
- Dra. Elia Cano (asesoría)
- Dr. Carlos Rovetto (colaboración)
- SENACYT Panamá


⭐ Si este proyecto te resultó útil, considera darle una estrella en GitHub.