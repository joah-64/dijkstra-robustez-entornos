import heapq

def dijkstra(n, W):
    """
    Implementación del Algoritmo 4.3 (Dijkstra) basada en el texto original.
    
    Parámetros:
      n : int -> Número de vértices en el grafo (de 1 a n).
      W : list[list] -> Matriz de adyacencia de tamaño (n+1) x (n+1).
                        W[i][j] representa el peso de la arista del vértice i al j.
                        Usa float('inf') para representar la ausencia de arista.
    
    Retorna:
      F : set -> Conjunto de tuplas (aristas) que forman los caminos mínimos.
    """
    # F = ∅; Inicializa el conjunto de aristas vacío
    F = set()
    
    # Índices touch y length definidos de 2..n (usamos tamaño n + 1 para indexar de 1 a n)
    touch = [0] * (n + 1)
    length = [0] * (n + 1)
    
    # Para todos los vértices, se inicializa v1 como el último vértice visitado
    # y la longitud inicial como el peso directo desde v1.
    for i in range(2, n + 1):
        touch[i] = 1
        length[i] = W[1][i]
        
    # Repetir (n - 1) veces para añadir todos los vértices restantes a Y
    for _ in range(n - 1):
        min_val = float('inf')
        vnear = -1
        
        # Verificar cada vértice para encontrar el que tenga el camino más corto
        for i in range(2, n + 1):
            if 0 <= length[i] < min_val:
                min_val = length[i]
                vnear = i
        
        # Guardar la arista correspondiente en el conjunto F
        # e = arista desde el vértice indexado por touch[vnear] hacia el vértice vnear
        e = (touch[vnear], vnear)
        F.add(e)
        
        # Para cada vértice que no está en Y, actualizar su camino más corto
        for i in range(2, n + 1):
            if length[vnear] + W[vnear][i] < length[i]:
                length[i] = length[vnear] + W[vnear][i]
                touch[i] = vnear
                
        # Marcar el vértice 'vnear' como añadido a Y asignándole -1
        length[vnear] = -1
        
    return F

def dijkstra_super(G, inicio, weight="length"):
    """
    Implementación manual de Dijkstra para grafos OSMnx/NetworkX.

    Parámetros
    ----------
    G : MultiDiGraph
        Grafo de OSMnx.

    inicio : int
        Nodo inicial REAL del grafo.

    weight : str
        Peso a utilizar:
        "length"
        "travel_time"
        etc.

    Retorna
    -------
    distancias : dict
        Distancia mínima desde inicio hacia cada nodo.

    caminos : dict
        Camino reconstruido hacia cada nodo.
    """

    # =====================================================
    # CONVERSIÓN DE NODOS
    # =====================================================

    nodes = list(G.nodes)

    node_to_idx = {
        node: i + 1
        for i, node in enumerate(nodes)
    }

    idx_to_node = {
        i + 1: node
        for i, node in enumerate(nodes)
    }

    n = len(nodes)

    # =====================================================
    # MATRIZ DE ADYACENCIA
    # =====================================================

    W = [
        [float("inf")] * (n + 1)
        for _ in range(n + 1)
    ]

    # diagonal = 0
    for i in range(1, n + 1):
        W[i][i] = 0

    # llenar matriz
    for u, v, k, data in G.edges(keys=True, data=True):

        i = node_to_idx[u]
        j = node_to_idx[v]

        peso = data.get(weight, float("inf"))

        # por si existen múltiples aristas
        W[i][j] = min(W[i][j], peso)

    # =====================================================
    # INICIO
    # =====================================================

    start = node_to_idx[inicio]

    # =====================================================
    # ESTRUCTURAS
    # =====================================================

    touch = [0] * (n + 1)

    length = [float("inf")] * (n + 1)

    parent = [0] * (n + 1)

    # inicialización
    for i in range(1, n + 1):

        touch[i] = start

        length[i] = W[start][i]

        if W[start][i] < float("inf"):
            parent[i] = start

    length[start] = -1

    # =====================================================
    # DIJKSTRA
    # =====================================================

    for _ in range(n - 1):

        min_val = float("inf")

        vnear = -1

        # encontrar nodo más cercano
        for i in range(1, n + 1):

            if 0 <= length[i] < min_val:

                min_val = length[i]

                vnear = i

        # si ya no hay alcanzables
        if vnear == -1:
            break

        # relajación
        for i in range(1, n + 1):

            if length[vnear] + W[vnear][i] < length[i]:

                length[i] = (
                    length[vnear]
                    + W[vnear][i]
                )

                touch[i] = vnear

                parent[i] = vnear

        # marcar visitado
        length[vnear] = -1

    # =====================================================
    # DISTANCIAS REALES
    # =====================================================

    distancias = {}

    for i in range(1, n + 1):

        nodo_real = idx_to_node[i]

        if length[i] == -1:
            distancias[nodo_real] = min_val
        else:
            distancias[nodo_real] = length[i]

    # =====================================================
    # RECONSTRUCCIÓN DE CAMINOS
    # =====================================================

    caminos = {}

    for i in range(1, n + 1):

        if i == start:
            continue

        if parent[i] == 0:
            continue

        camino = []

        actual = i

        while actual != start:

            camino.append(
                idx_to_node[actual]
            )

            actual = parent[actual]

        camino.append(
            idx_to_node[start]
        )

        camino.reverse()

        caminos[
            idx_to_node[i]
        ] = camino

    return distancias, caminos


# ==========================================
# Dijkstra.py
# ==========================================

import heapq

# ==========================================
# PESO DINÁMICO
# ==========================================


# ==========================================
# Dijkstra.py
# ==========================================

import heapq

from Mundo import peso_dinamico


# ==========================================
# DIJKSTRA HYPER DINÁMICO
# ==========================================

def dijkstra_hyper2(G,origen,destino=None,weight="length"):
    """
    Implementación eficiente de Dijkstra para grafos OSMnx.

    Parámetros
    ----------
    G : MultiDiGraph
        Grafo de OSMnx.

    origen : int
        Nodo origen.

    destino : int or None
        Nodo destino.
        Si se proporciona, el algoritmo termina
        apenas encuentra el camino óptimo.

    weight : str
        Peso de las aristas:
        "length"
        "travel_time"
        etc.

    Retorna
    -------
    ruta : list
        Ruta reconstruida desde origen hasta destino.

    distancias : dict
        Distancias mínimas desde origen.

    padres : dict
        Padres usados para reconstrucción.
    """
    grafo = {}

    for u, v, k, data in G.edges(
        keys=True,
        data=True
    ):

        peso = data.get(
            weight,
            float("inf")
        )

        if u not in grafo:
            grafo[u] = []

        grafo[u].append(
            (v, peso)
        )

    distancias = {
        nodo: float("inf")
        for nodo in G.nodes
    }

    distancias[origen] = 0
    padres = {}
    heap = [(0, origen)]

    # ==========================================
    # DIJKSTRA
    # ==========================================

    while heap:

        distancia_actual, u = heapq.heappop(heap)

        # Ignorar entradas viejas
        if distancia_actual > distancias[u]:
            continue

        # Early stop
        if destino is not None and u == destino:
            break

        # Si el nodo no tiene vecinos
        if u not in grafo:
            continue

        # Revisar vecinos reales
        for vecino, peso in grafo[u]:

            nueva_distancia = (
                distancia_actual + peso
            )

            # Relajación
            if nueva_distancia < distancias[vecino]:

                distancias[vecino] = (
                    nueva_distancia
                )

                padres[vecino] = u

                heapq.heappush(
                    heap,
                    (
                        nueva_distancia,
                        vecino
                    )
                )

    # ==========================================
    # RECONSTRUCCIÓN DE RUTA
    # ==========================================

    ruta = []

    # Si se pidió destino
    if destino is not None:

        # No existe camino
        if destino not in padres and destino != origen:

            return None, distancias, padres

        actual = destino

        while actual != origen:

            ruta.append(actual)

            actual = padres[actual]

        ruta.append(origen)

        ruta.reverse()

    return ruta, distancias, padres




def dijkstra_hyper(
    G_adj,
    nodes,
    origen,
    destino=None,
    estado=None
):
   

    # ======================================
    # DISTANCIAS
    # ======================================

    distancias = {
        nodo: float("inf")
        for nodo in nodes
    }

    distancias[origen] = 0

    padres = {}

    heap = [(0, origen)]

    # ======================================
    # DIJKSTRA
    # ======================================

    while heap:

        distancia_actual, u = heapq.heappop(heap)

        # ==================================
        # IGNORAR ENTRADAS VIEJAS
        # ==================================

        if distancia_actual > distancias[u]:

            continue

        # ==================================
        # EARLY STOP
        # ==================================

        if destino is not None and u == destino:

            break

        # ==================================
        # SI NO TIENE VECINOS
        # ==================================

        if u not in G_adj:

            continue

        # ==================================
        # RELAJACIÓN
        # ==================================

        for vecino, data in G_adj[u]:
            peso = peso_dinamico(
                u,
                vecino,
                data,
                estado
            )

            nueva_distancia = (
                distancia_actual + peso
            )

            if nueva_distancia < distancias[vecino]:

                distancias[vecino] = nueva_distancia

                padres[vecino] = u

                heapq.heappush(
                    heap,
                    (
                        nueva_distancia,
                        vecino
                    )
                )

    # ======================================
    # RECONSTRUCCIÓN
    # ======================================

    ruta = []

    if destino is not None:

        # ==================================
        # NO EXISTE CAMINO
        # ==================================

        if (

            destino not in padres

            and destino != origen
        ):

            return [], distancias, padres

        actual = destino

        while actual != origen:

            ruta.append(actual)

            actual = padres[actual]

        ruta.append(origen)

        ruta.reverse()

    return ruta, distancias, padres