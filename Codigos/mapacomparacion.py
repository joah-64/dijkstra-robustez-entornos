# =========================================================
# mapas_comparativos.py
# =========================================================

import pandas as pd
import ast
import os
import webbrowser
import osmnx as ox
import folium

# =========================================================
# CARGAR GRAFO
# =========================================================

print("Cargando mapa...")

G = ox.load_graphml(
    "mty_metropolitana.graphml"
)

G = ox.project_graph(G)

print("Mapa cargado correctamente.")

# =========================================================
# CARGAR CSV
# =========================================================

df = pd.read_csv(
    "prueba.csv"
)

# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def GraficarComparativo(
    G,
    ruta_real,
    ruta_fantasma,
    archivo="comparacion"
):

    extension = "html"

    nombre_final = f"{archivo}.{extension}"

    # =========================================
    # GeoDataFrames
    # =========================================

    route_real_gdf = ox.routing.route_to_gdf(
        G,
        ruta_real
    )

    route_fantasma_gdf = ox.routing.route_to_gdf(
        G,
        ruta_fantasma
    )

    # =========================================
    # MAPA
    # =========================================

    m = folium.Map(
        location=[25.67, -100.31],
        zoom_start=11
    )

    # =========================================
    # RUTA REAL
    # =========================================

    folium.GeoJson(
        route_real_gdf.geometry,
        style_function=lambda x: {
            "color": "red",
            "weight": 6
        },
        tooltip="Conductor REAL"
    ).add_to(m)

    # =========================================
    # RUTA FANTASMA
    # =========================================

    folium.GeoJson(
        route_fantasma_gdf.geometry,
        style_function=lambda x: {
            "color": "blue",
            "weight": 6
        },
        tooltip="Conductor FANTASMA"
    ).add_to(m)

    # =========================================
    # GUARDAR
    # =========================================

    m.save(nombre_final)

    ruta_absoluta = os.path.abspath(
        nombre_final
    )

    webbrowser.open(
        f"file://{ruta_absoluta}"
    )

    print(
        f"Archivo HTML guardado como: "
        f"{nombre_final} 💾"
    )

    print(
        "Archivo abierto en el navegador ✅"
    )

# =========================================================
# GENERAR TODOS
# =========================================================

for i, fila in df.iterrows():

    print()

    print(
        f"Generando mapa {i+1}/{len(df)}"
    )

    # =========================================
    # Convertir string -> lista
    # =========================================

    ruta_real = ast.literal_eval(
        fila["ruta_real"]
    )

    ruta_fantasma = ast.literal_eval(
        fila["ruta_fantasma"]
    )

    # =========================================
    # Nombre archivo
    # =========================================

    nombre = (

        f"comparacion_"

        f"hora_{fila['hora']}_"

        f"semilla_{fila['semilla']}"
    )

    # =========================================
    # Crear mapa
    # =========================================

    GraficarComparativo(
        G,
        ruta_real,
        ruta_fantasma,
        nombre
    )

print()
print("Todos los mapas fueron generados 🚀")