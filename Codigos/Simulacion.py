# =========================================================
# Simulacion.py
# =========================================================

import numpy as np
import time
import gc
import random
import osmnx as ox
from Mundo import *
from Conductores import *
from Dijkstra import dijkstra_hyper

# =========================================================
# ESCENARIO AISLADO
# =========================================================


def preparar_grafo(G):

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

        distance_km = data.get("length", 1) / 1000

        travel_time = distance_km / speed

        data["travel_time"] = max(
            travel_time,
            0.0001
        )

    return G





G = None
G_adj = None
def inicializar_worker():

    global G
    print()
    inicio_total = time.perf_counter()

    
    if G is None:
        print("Worker cargando mapa...")

        G = ox.load_graphml(
            "mty_metropolitana.graphml"
        )

        G = ox.project_graph(G)

        G = preparar_grafo(G)
    global G_adj

    G_adj = {}

    for u, v, k, data in G.edges(
        keys=True,
        data=True
    ):

        if u not in G_adj:

            G_adj[u] = []

        G_adj[u].append(
            (v, data)
        )
    fin_total = time.perf_counter()
    print(
        f"Tiempo total de cargar grafos:",
        round(fin_total - inicio_total,2),
        "segundos"
    )    




def ejecutar_escenario_aislado(

    hora,
    semilla,origen=None,destino=None

):
    global G
    try:

        rng = np.random.default_rng(semilla)

        # ========================================
        # NODOS ALEATORIOS
        # ========================================

        nodes = list(G.nodes)
        if origen==None:
            origen = random.choice(nodes)
        if destino==None:
            destino = random.choice(nodes)

        while destino == origen:

            destino = random.choice(nodes)

        # ========================================
        # ESTADO INICIAL
        # ========================================

        estado = crear_estado_inicial(
            rng,
            hora
        )

        # ========================================
        # CONDUCTORES
        # ========================================

        conductor_real = Conductor(
            origen,
            destino,
            fantasma=False
        )

        conductor_fantasma = Conductor(
            origen,
            destino,
            fantasma=True
        )

        turnos = 0

        MAX_TURNOS = 200

        # ========================================
        # LOOP PRINCIPAL
        # ========================================

        while (

            not conductor_real.llego

            and not conductor_fantasma.llego

            and turnos < MAX_TURNOS

        ):

            turnos += 1
            # ====================================
            # Dijkstra real
            # ====================================
            
            if conductor_real.arista_actual is not None:

                _, siguiente = conductor_real.arista_actual

                nodo_inicio_real = siguiente

            else:

                nodo_inicio_real = conductor_real.nodo_actual





            inicio_real = time.perf_counter()

            ruta_real, _, _ = dijkstra_hyper(
                G_adj,
                G.nodes,
                nodo_inicio_real,
                destino,
                estado
            )
    

            fin_real = time.perf_counter()

            tiempo_dijkstra_real = (

                fin_real - inicio_real
            )
            reaccion = rng.exponential(2)

            duracion_turno_real = (

                tiempo_dijkstra_real
                + reaccion
            )

            conductor_real.actualizar_ruta(
                ruta_real
            )
            # ====================================
            # Dijkstra  fantasma
            # ====================================
            inicio_f = time.perf_counter()

            if conductor_fantasma.arista_actual is not None:

                _, siguiente = conductor_fantasma.arista_actual

                nodo_inicio_fanta = siguiente

            else:

                nodo_inicio_fanta = conductor_fantasma.nodo_actual




            ruta_f, _, _ = dijkstra_hyper(
                G_adj,
                G.nodes,
                nodo_inicio_fanta,
                destino,
                estado
            )

            fin_f = time.perf_counter()

            tiempo_f = (

                fin_f - inicio_f
            )

            conductor_fantasma.actualizar_ruta(
                ruta_f
            )
            # ====================================
            # FANTASMA se mueve
            # ====================================
            conductor_fantasma.mover(

                tiempo_f,

                G,

                estado,

                peso_dinamico
            )


            # ====================================
            # ACTUALIZAR MUNDO
            # ====================================

            estado = actualizar_mundo(

                G,
                estado,
                rng,
                hora
            )

            # ====================================
            # Real se mueve
            # ====================================
            conductor_real.mover(

                duracion_turno_real,

                G,

                estado,

                peso_dinamico
            )





        # ========================================
        # ERROR RELATIVO
        # ========================================

        if conductor_fantasma.tiempo_total > 0:

            error_relativo = (

                (
                    conductor_real.tiempo_total

                    -

                    conductor_fantasma.tiempo_total
                )

                /

                conductor_fantasma.tiempo_total
            )

        else:

            error_relativo = 0

        # ========================================
        # RESULTADO
        # ========================================

        resultado = {

            "hora": hora,

            "semilla": semilla,

            "tiempo_real":
                conductor_real.tiempo_total,

            "tiempo_fantasma":
                conductor_fantasma.tiempo_total,

            "error_relativo":
                error_relativo,

            "recalculos_real":
                conductor_real.recalculos,

            "recalculos_fantasma":
                conductor_fantasma.recalculos,

            "turnos":
                turnos,

            "ruta_real":
                conductor_real.historial_nodos,

            "ruta_fantasma":
                conductor_fantasma.historial_nodos
        
        }

        del estado

        gc.collect()

        return resultado

    except Exception as e:

        return {

            "hora": hora,

            "semilla": semilla,

            "error": str(e)
        }