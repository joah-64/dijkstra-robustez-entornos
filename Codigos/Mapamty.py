import osmnx as ox
import networkx as nx
from pyproj import Transformer
import folium
from Dijkstra import dijkstra_hyper
from Dijkstra import dijkstra_hyper2
import pandas as pd
from colorama import Fore, Back, Style, init
import webbrowser
import os
from datetime import datetime
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import time
from multiprocessing import Pool
from Simulacion import ejecutar_escenario_aislado
from Simulacion import inicializar_worker
from Analisis import *
init(autoreset=True)
CIAN_BRILLANTE = Fore.CYAN + Style.BRIGHT
GRIS = Fore.LIGHTBLACK_EX
NEGRILLA = Style.BRIGHT
VERDE = Fore.GREEN
AMARILLO = Fore.YELLOW
RESET = Style.RESET_ALL
CIAN = Fore.CYAN + Style.BRIGHT
ROJO = Fore.RED

def Ruta_Corta(G,orig,dest):
    # convertir coordenadas al CRS del grafo
    transformer = Transformer.from_crs(
        "epsg:4326",
        G.graph["crs"],
        always_xy=True
    )
    orig_x, orig_y = transformer.transform(orig[1], orig[0])
    dest_x, dest_y = transformer.transform(dest[1], dest[0])
    # nodos más cercanos
    orig_node = ox.distance.nearest_nodes(G, orig_x, orig_y)
    dest_node = ox.distance.nearest_nodes(G, dest_x, dest_y)

    for u, v, k, data in G.edges(keys=True, data=True):

        highway = data.get("highway", "")

        if isinstance(highway, list):
            highway = highway[0]

        if highway == "motorway":
            speed = 100

        elif highway == "primary":
            speed = 70

        elif highway == "secondary":
            speed = 50

        elif highway == "residential":
            speed = 30

        else:
            speed = 40

        data["speed_kph"] = speed

    for u, v, k, data in G.edges(keys=True, data=True):

        distance_km = data["length"] / 1000

        speed = data["speed_kph"]

        travel_time = distance_km / speed

        data["travel_time"] = travel_time


    ###
    inicio_DH = time.perf_counter()
    route, distancias, padres = dijkstra_hyper2(G,orig_node,dest_node,weight="travel_time")
    fin_DH = time.perf_counter()
    tiempo_total_DH = fin_DH - inicio_DH
    print(f"⏱️ Tiempo de ejecución de dijkstra hyper: {tiempo_total_DH:.4f} segundos")
    ###
    #print("Distancia total:")

    #print(distancias[dest_node],"metros")
    #print("route:")
    #print(route)
    #====================
    #MOSTRAR lo siguiente
    #====================
    #ox.plot_graph_route(G,route,route_linewidth=4,node_size=0)
    return route
def GraficarComparacion(
    G,
    ruta_real,
    ruta_fantasma,
    archivo="comparacion"
):
    if len(ruta_real) < 2 or len(ruta_fantasma) < 2:

        print("❌ Ruta inválida")
        return
    m = folium.Map(
        location=[25.67, -100.31],
        zoom_start=11
    )

    # ======================================
    # RUTA REAL
    # ======================================

    gdf_real = ox.routing.route_to_gdf(
        G,
        ruta_real
    )

    folium.GeoJson(

        gdf_real.geometry,

        style_function=lambda x: {

            "color": "red",
            "weight": 6
        }

    ).add_to(m)

    # ======================================
    # RUTA FANTASMA
    # ======================================

    gdf_f = ox.routing.route_to_gdf(
        G,
        ruta_fantasma
    )

    folium.GeoJson(

        gdf_f.geometry,

        style_function=lambda x: {

            "color": "blue",
            "weight": 6
        }

    ).add_to(m)

    # ======================================
    # GUARDAR
    # ======================================

    nombre_final = f"{archivo}.html"

    m.save(nombre_final)

    ruta_absoluta = os.path.abspath(
        nombre_final
    )

    webbrowser.open(
        f"file://{ruta_absoluta}"
    )

    print("Mapa comparativo guardado")
def Graficar(G,route,archivo="ruta"):
    extension="html"
    nombre_final = f"{archivo}.{extension}"
    route_gdf = ox.routing.route_to_gdf(G, route)
    m = folium.Map(
        location=[25.67, -100.31],
        zoom_start=11
    )
    folium.GeoJson(
        route_gdf.geometry
    ).add_to(m)

    folium.GeoJson(
        route_gdf.geometry,
        style_function=lambda x: {
            "color": "red",
            "weight": 6
        }
    ).add_to(m)
    m.save(nombre_final)
    ruta_absoluta = os.path.abspath(nombre_final)
    webbrowser.open(f"file://{ruta_absoluta}")
    print(Fore.GREEN +f"Archivo HTML guardado como: {nombre_final} 💾" )
    print(Fore.GREEN +"Archivo abierto en el navegador"+"✅")
def GuardarRutaExcel(G,route,archivo="ruta"):
    
    # --- TU LÓGICA INTACTA (Procesamiento de datos) ---
    extension = "xlsx"
    nombre_final = f"{archivo}.{extension}"
    datos = []

    total_distance = 0
    total_time = 0
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G.get_edge_data(u, v)
        edge = edge_data[0]
        street_name = edge.get("name", "Sin nombre")
        length = edge.get("length", 0)
        speed = edge.get("speed_kph", "N/A")
        travel_time = edge.get("travel_time", 0)
        total_distance += length
        total_time += travel_time
        datos.append({
            "Nodo Origen": u,
            "Nodo Destino": v,
            "Calle": street_name,
            "Distancia (m)": round(length, 2),
            "Velocidad (km/h)": speed,
            "Tiempo (min)": round(travel_time * 60, 2)
        })
    df = pd.DataFrame(datos)

    resumen = pd.DataFrame([{
        "Distancia Total (km)": round(total_distance / 1000, 2),
        "Tiempo Total (min)": round(total_time * 60, 2),
        "Cantidad de Nodos": len(G.nodes),
        "Cantidad de Aristas": len(G.edges)
    }])

    with pd.ExcelWriter(nombre_final, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Ruta", index=False)
        resumen.to_excel(writer, sheet_name="Resumen", index=False)
        workbook = writer.book
        azul_oscuro_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        gris_claro_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid") 
        fuente_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        fuente_datos = Font(name="Segoe UI", size=10, bold=False, color="000000")
        borde_sutil = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )
        for nombre_pestana in ["Ruta", "Resumen"]:
            ws = writer.sheets[nombre_pestana]
            for fila_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column), start=1):
                for cell in row:
                    cell.border = borde_sutil
                    
                    if fila_idx == 1:
                        cell.font = fuente_header
                        cell.fill = azul_oscuro_fill
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                    else:
                        cell.font = fuente_datos
                        if isinstance(cell.value, (int, float)):
                            cell.alignment = Alignment(horizontal="center", vertical="center")
                        else:
                            cell.alignment = Alignment(horizontal="left", vertical="center")
                        if fila_idx % 2 == 0:
                            cell.fill = gris_claro_fill
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    print("Distancia Total (km) :", round(total_distance / 1000, 2),)
    print("Tiempo Total (min):", round(total_time * 60,2))
    print("Cantidad de Nodos", len(G.nodes))
    print("Cantidad de Aristas", len(G.edges))


    print(Fore.GREEN + f"Excel guardado como: {nombre_final} 💾")
def Manual():
    nombre_base = "RUTA"
    ahora = datetime.now()
    fecha_formateada = ahora.strftime("%Y-%m-%d_%H-%M-%S")
    nombre_final = f"{nombre_base}_{fecha_formateada}"
    print(f"\n{CIAN_BRILLANTE}🗺️  BIENVENIDO AL MODO MANUAL")
    print(f"{GRIS}   Encontrar la ruta más corta desde una localización hacia otra\n")

    print(f"{NEGRILLA}¿Qué tipo de dirección quisiera añadir?")
    print(f" {AMARILLO}• [0]{RESET} Coordenadas")
    print(f" {AMARILLO}• [1]{RESET} Dirección escrita")
    if (input(f"\n{Fore.CYAN}➔ Selección: {RESET}") == 0):
        Origen = input(f"\n📍 {NEGRILLA}Ingrese las coordenadas de origen:{RESET} ")
        Origen = tuple(map(float, Origen.split(",")))
        Destino = input(f"🏁 {NEGRILLA}Ingrese las coordenadas del destino:{RESET} ")
        Destino = tuple(map(float, Destino.split(",")))
    else:
        Origen = input(f"\n📍 {NEGRILLA}Ingrese la ubicación de origen:{RESET} ")
        Destino = input(f"🏁 {NEGRILLA}Ingrese la ubicación del destino:{RESET} ")
        Origen = ox.geocode(Origen)
        Destino = ox.geocode(Destino)
        print(f"\n{VERDE}✔ Coordenadas de Origen encontradas: {RESET}{Origen}")
        print(f"{VERDE}✔ Coordenadas de Destino encontradas: {RESET}{Destino}\n")
            #Ejemplo:
        #Bosque de Mora, Bosques de San Miguel, Apodaca, Nuevo León, 66647, Mexico
        #Ciudad Universitaria UANL, San Nicolas, Nuevo Leon, Mexico
    Ruta=Ruta_Corta(G,Origen,Destino)     
    Graficar(G,Ruta,nombre_final)
    GuardarRutaExcel(G,Ruta,nombre_final)

from multiprocessing import Pool
from Simulacion import ejecutar_escenario_aislado

from Analisis import (
    guardar_resultados_csv,
    guardar_resultados_excel,
    generar_resumen_estadistico,
    generar_histogramas
)

def wrapper_escenario(args):

    return ejecutar_escenario_aislado(*args)


def Experimento():

    print(f"\n{CIAN_BRILLANTE}🧪 INICIANDO SIMULACIÓN MONTE CARLO")

    # ============================================
    # CONFIGURACIÓN PEQUEÑA
    # ============================================

    TOTAL_DIAS = 1

    HORAS_ANALIZADAS = [4,8,20]

    PROCESOS = 3

    tareas = []

    # ============================================
    # CREAR ESCENARIOS
    # ============================================

    for dia in range(1, TOTAL_DIAS + 1):

        for hora in HORAS_ANALIZADAS:

            semilla = int(f"{dia}{hora:02d}")

            tareas.append(
                (
                    hora,
                    semilla
                )
            )

    total_escenarios = len(tareas)

    print(f"{VERDE}✔ Escenarios:{RESET} {total_escenarios}")

    resultados = []

    inicio_total = time.perf_counter()

    # ============================================
    # MONTE CARLO
    # ============================================

    with Pool(processes=PROCESOS,initializer=inicializar_worker) as pool:
        for i, resultado in enumerate(

            pool.imap_unordered(
                wrapper_escenario,
                tareas
            ),

            start=1
        ):

            resultados.append(resultado)

            print()

            print(
                f"{AMARILLO}Simulación "
                f"{i}/{total_escenarios}{RESET}"
            )

            # ====================================
            # MOSTRAR RESULTADO
            # ====================================

            if "error" in resultado:

                print(
                    f"{ROJO}ERROR:{RESET}",
                    resultado["error"]
                )

            else:

                print(
                    f"{VERDE}Error relativo:{RESET}",
                    round(
                        resultado["error_relativo"],
                        4
                    )
                )

                print(
                    f"{VERDE}Tiempo real:{RESET}",
                    round(
                        resultado["tiempo_real"],
                        4
                    )
                )

                print(
                    f"{VERDE}Tiempo fantasma:{RESET}",
                    round(
                        resultado["tiempo_fantasma"],
                        4
                    )
                )

    # ============================================
    # FINAL
    # ============================================
    fin_total = time.perf_counter()

    print()
    print(
        f"{VERDE}Tiempo total:{RESET}",
        round(fin_total - inicio_total,2),
        "segundos"
    )

    # ============================================
    # FILTRAR RESULTADOS VÁLIDOS
    # ============================================

    resultados_validos = [

        r for r in resultados

        if "error_relativo" in r
    ]

    # ============================================
    # GUARDAR
    # ============================================

    guardar_resultados_csv(
        resultados_validos,
        "prueba.csv"
    )

    guardar_resultados_excel(
        resultados_validos,
        "prueba.xlsx"
    )

    # ============================================
    # RESUMEN
    # ============================================
    if len(resultados_validos) == 0:

        print(f"{ROJO}❌ Todas las simulaciones fallaron{RESET}")

        return
    resumen = generar_resumen_estadistico(
        resultados_validos
    )

    print()

    print(
        f"{CIAN}Promedio Error:{RESET}",
        round(
            resumen["promedio_error_relativo"],
            4
        )
    )

    print(
        f"{CIAN}Máximo Error:{RESET}",
        round(
            resumen["max_error_relativo"],
            4
        )
    )

    generar_histogramas(
        resultados_validos,
        "graficas_prueba"
    )
    peor = max(
    resultados_validos,
    key=lambda x: x["error_relativo"]
)
    mejor = min(
    resultados_validos,
    key=lambda x: x["error_relativo"]
)
    GraficarComparacion(G,peor["ruta_real"],peor["ruta_fantasma"],"comparacion_peor")
    GraficarComparacion(G,mejor["ruta_real"],mejor["ruta_fantasma"],"comparacion_mejor")
    print()

    print(f"{VERDE}🏁 PRUEBA TERMINADA{RESET}")

def Experimento_Manual():

    print(f"\n{CIAN_BRILLANTE}🧪 INICIANDO SIMULACIÓN MANUAL")

    # ============================================
    # CONFIGURACIÓN PEQUEÑA
    # ============================================

    TOTAL_DIAS = 1
    print("Ingrese la hora:")
    x=input("<4,8,20>")


    print(f"{GRIS}   Encontrar la ruta más corta desde una localización hacia otra\n")

    print(f"{NEGRILLA}¿Qué tipo de dirección quisiera añadir?")
    print(f" {AMARILLO}• [0]{RESET} Coordenadas")
    print(f" {AMARILLO}• [1]{RESET} Dirección escrita")
    if (input(f"\n{Fore.CYAN}➔ Selección: {RESET}") == 0):
        Origen = input(f"\n📍 {NEGRILLA}Ingrese las coordenadas de origen:{RESET} ")
        Origen = tuple(map(float, Origen.split(",")))
        Destino = input(f"🏁 {NEGRILLA}Ingrese las coordenadas del destino:{RESET} ")
        Destino = tuple(map(float, Destino.split(",")))
    else:
        Origen = input(f"\n📍 {NEGRILLA}Ingrese la ubicación de origen:{RESET} ")
        Destino = input(f"🏁 {NEGRILLA}Ingrese la ubicación del destino:{RESET} ")
        Origen = ox.geocode(Origen)
        Destino = ox.geocode(Destino)
        print(f"\n{VERDE}✔ Coordenadas de Origen encontradas: {RESET}{Origen}")
        print(f"{VERDE}✔ Coordenadas de Destino encontradas: {RESET}{Destino}\n")
            #Ejemplo:
        #Bosque de Mora, Bosques de San Miguel, Apodaca, Nuevo León, 66647, Mexico
        #Ciudad Universitaria UANL, San Nicolas, Nuevo Leon, Mexico


        # convertir coordenadas al CRS del grafo
    transformer = Transformer.from_crs(
        "epsg:4326",
        G.graph["crs"],
        always_xy=True
    )
    orig_x, orig_y = transformer.transform(Origen[1], Origen[0])
    dest_x, dest_y = transformer.transform(Destino[1], Destino[0])
    # nodos más cercanos
    orig_node = ox.distance.nearest_nodes(G, orig_x, orig_y)
    dest_node = ox.distance.nearest_nodes(G, dest_x, dest_y)

    HORAS_ANALIZADAS = [int(x)]

    PROCESOS = 1

    tareas = []

    # ============================================
    # CREAR ESCENARIOS
    # ============================================

    for dia in range(1, TOTAL_DIAS + 1):

        for hora in HORAS_ANALIZADAS:

            semilla = int(f"{dia}{hora:02d}")

            tareas.append(
                (
                    hora,
                    semilla,orig_node,dest_node
                )
            )

    total_escenarios = len(tareas)

    print(f"{VERDE}✔ Escenarios:{RESET} {total_escenarios}")

    resultados = []

    inicio_total = time.perf_counter()

    # ============================================
    # MONTE CARLO
    # ============================================

    with Pool(processes=PROCESOS,initializer=inicializar_worker) as pool:
        for i, resultado in enumerate(

            pool.imap_unordered(
                wrapper_escenario,
                tareas
            ),

            start=1
        ):

            resultados.append(resultado)

            print()

            print(
                f"{AMARILLO}Simulación "
                f"{i}/{total_escenarios}{RESET}"
            )

            # ====================================
            # MOSTRAR RESULTADO
            # ====================================

            if "error" in resultado:

                print(
                    f"{ROJO}ERROR:{RESET}",
                    resultado["error"]
                )

            else:

                print(
                    f"{VERDE}Error relativo:{RESET}",
                    round(
                        resultado["error_relativo"],
                        4
                    )
                )

                print(
                    f"{VERDE}Tiempo real:{RESET}",
                    round(
                        resultado["tiempo_real"],
                        4
                    )
                )

                print(
                    f"{VERDE}Tiempo fantasma:{RESET}",
                    round(
                        resultado["tiempo_fantasma"],
                        4
                    )
                )

    # ============================================
    # FINAL
    # ============================================
    fin_total = time.perf_counter()

    print()
    print(
        f"{VERDE}Tiempo total:{RESET}",
        round(fin_total - inicio_total,2),
        "segundos"
    )

    # ============================================
    # FILTRAR RESULTADOS VÁLIDOS
    # ============================================

    resultados_validos = [

        r for r in resultados

        if "error_relativo" in r
    ]

    # ============================================
    # GUARDAR
    # ============================================

    guardar_resultados_csv(
        resultados_validos,
        "prueba.csv"
    )

    guardar_resultados_excel(
        resultados_validos,
        "prueba.xlsx"
    )

    # ============================================
    # RESUMEN
    # ============================================
    if len(resultados_validos) == 0:

        print(f"{ROJO}❌ Todas las simulaciones fallaron{RESET}")

        return
    resumen = generar_resumen_estadistico(
        resultados_validos
    )

    print()

    print(
        f"{CIAN}Promedio Error:{RESET}",
        round(
            resumen["promedio_error_relativo"],
            4
        )
    )

    print(
        f"{CIAN}Máximo Error:{RESET}",
        round(
            resumen["max_error_relativo"],
            4
        )
    )

    generar_histogramas(
        resultados_validos,
        "graficas_prueba"
    )
    peor = max(
    resultados_validos,
    key=lambda x: x["error_relativo"]
)
    mejor = min(
    resultados_validos,
    key=lambda x: x["error_relativo"]
)
    GraficarComparacion(G,peor["ruta_real"],peor["ruta_fantasma"],"comparacion_peor")
    GraficarComparacion(G,mejor["ruta_real"],mejor["ruta_fantasma"],"comparacion_mejor")
    print()

    print(f"{VERDE}🏁 PRUEBA TERMINADA{RESET}")

if __name__ == "__main__":
    #Importar mapa
    print("Cargando...")
    G = ox.load_graphml("mty_metropolitana.graphml")
    print("Proyectando el area metropolitana...")
    G = ox.project_graph(G)
    print(Fore.GREEN + "Carga completa")
    nodes = list(G.nodes)
    n = len(nodes)
    print ("Numero de nodos:",n)
    while(True):
        print(f"\n{NEGRILLA}═════════════════════════════════════════════════════════")
        print(f"✨ {CIAN}SISTEMA DE OPTIMIZACIÓN DE RUTAS CON DIJKSTRA HYPER{RESET}")
        print(f"{NEGRILLA}═════════════════════════════════════════════════════════")
        
        # Pregunta inicial: mantiene la lógica exacta del "s"
        if(input(f"¿Desea buscar rutas cortas? ({VERDE}s{RESET}/{ROJO}n{RESET}): ") == "s"):
            
            # Desplegamos las opciones de manera ordenada antes del input
            print(f"\n{NEGRILLA}🛠️  SELECCIONE EL MODO DE OPERACIÓN:")
            print(f" {AMARILLO}• [0]{RESET} Modo Manual")
            print(f" {AMARILLO}• [1]{RESET} Modo Experimento")
            print(f" {AMARILLO}• [2]{RESET} Modo Experimento Manual")
            # Pregunta de selección: mantiene la lógica exacta del "0"
            decision=input(f"\n{CIAN}➔ Ingrese su opción <0/1/2>: {RESET}")
            if( decision== "0"):
                Manual()
            elif( decision== "1"):
                Experimento()
            else:
                Experimento_Manual()
        else:
            # Mensaje estético de salida antes de romper el bucle
            print(f"\n{ROJO}❌ Saliendo del sistema... ¡Hasta luego!{RESET}\n")
            break