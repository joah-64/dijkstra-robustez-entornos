# Mundo.py

import random

from Distribuciones_probabilidad import (
    generar_accidentes_poisson,
    factor_trafico_normal,
    factor_trafico_lognormal,
    duracion_accidente_weibull,
    evento_extremo_cauchy,
    clima_markov,
    tipo_dia_markov
)
# =========================================================
# PESO DINÁMICO
# =========================================================
def peso_dinamico(
    u,
    v,
    data,
    estado

):

    # ============================================
    # TIEMPO BASE
    # ============================================

    tiempo = data.get(
        "travel_time",
        1.0
    )

    # ============================================
    # FACTOR GLOBAL DE TRÁFICO
    # ============================================

    tiempo *= estado.get("factor_trafico", 1.0)

    # ============================================
    # CLIMA
    # ============================================

    clima = estado["clima"]

    # 0 = soleado
    # 1 = lluvia
    # 2 = tormenta

    if clima == 1:

        tiempo *= 1.25

    elif clima == 2:

        tiempo *= 1.60

    # ============================================
    # HORA PICO
    # ============================================

    hora = estado["hora"]

    if hora == 4:

        tiempo *= 0.70

    elif hora == 7:

        tiempo *= 1.35

    elif hora == 8:

        tiempo *= 1.60

    elif hora == 9:

        tiempo *= 1.20

    elif hora == 10:

        tiempo *= 0.90

    elif hora == 12:

        tiempo *= 1.10

    elif hora == 14:

        tiempo *= 1.15

    elif hora == 16:

        tiempo *= 1.25

    elif hora == 18:

        tiempo *= 1.40

    elif hora == 20:

        tiempo *= 1.50

    # ============================================
    # ACCIDENTES ACTIVOS
    # ============================================

    accidentes = estado["accidentes"]

    if (u, v) in accidentes:

        severidad = accidentes[(u, v)]

        highway = data.get("highway", "")

        if isinstance(highway, list):

            highway = highway[0]

        if highway == "motorway":

            severidad *= 8

        elif highway == "primary":

            severidad *= 5

        elif highway == "secondary":

            severidad *= 3

        elif highway == "residential":

            severidad *= 1.5

        tiempo *= severidad
    # ============================================
    # EVENTOS EXTREMOS
    # ============================================

    if estado["evento_extremo"]:

        tiempo *= estado.get("factor_trafico", 1.0)

    # ============================================
    # SEGURIDAD
    # ============================================
    # ============================================
    # Temporal
    # ============================================
      

    turno = estado["turno"]
    highway = data.get("highway", "")
    if isinstance(highway, list):
        highway = highway[0]
    if (turno // 5) % 2 == 0:

        if highway == "motorway":

            tiempo *= 0.000001

        else:

            tiempo *= 1

    else:

        if highway == "motorway":

            tiempo *= 1

        else:

            tiempo *= 0.000001
    pesos = {

    0: {
        "motorway": 0.000001,
        "primary": 10,
        "secondary": 10,
        "residential": 10
    },

    1: {
        "motorway": 10,
        "primary": 10,
        "secondary": 10,
        "residential": 0.000001
    },

    2: {
        "motorway": 10,
        "primary": 0.000001,
        "secondary": 10,
        "residential": 10
    },

    3: {
        "motorway": 10,
        "primary": 10,
        "secondary": 0.000001,
        "residential": 10
    }
}

    fase = (turno // 5) % 4

    factor = pesos[fase].get(
        highway,
        10
    )

    tiempo *= factor



    return max(tiempo, 0.0001)
def obtener_factor_hora(hora):

    """
    Devuelve qué tan pesado está el tráfico
    dependiendo de la hora.
    """

    tabla = {

        4: 0.60,   # vacío
        5: 0.70,
        6: 0.90,

        7: 1.80,   # hora pico
        8: 2.20,
        9: 1.60,

        10: 0.90,
        11: 1.00,

        12: 1.30,
        13: 1.35,
        14: 1.40,

        15: 1.30,
        16: 1.50,
        17: 1.70,

        18: 1.60,
        19: 1.50,

        20: 2.00,

        21: 1.30,
        22: 0.90,
        23: 0.70
    }

    return tabla.get(hora, 1.0)

# Mundo.py
from Distribuciones_probabilidad import *
import random

def crear_estado_inicial(rng, hora):

    # ==============================
    # CLIMA INICIAL
    # ==============================

    clima = rng.choice([0,1,2])

    # ==============================
    # TIPO DE DÍA
    # ==============================

    tipo_dia = rng.choice([0,1,2])

    # ==============================
    # FACTOR SEGÚN HORA
    # ==============================

    if hora == 4:

        factor_hora = 0.6

    elif hora == 7:

        factor_hora = 1.8

    elif hora == 8:

        factor_hora = 2.2

    elif hora == 9:

        factor_hora = 1.5

    elif hora == 10:

        factor_hora = 0.9

    elif hora == 12:

        factor_hora = 1.2

    elif hora == 14:

        factor_hora = 1.3

    elif hora == 16:

        factor_hora = 1.4

    elif hora == 18:

        factor_hora = 1.7

    elif hora == 20:

        factor_hora = 2.0

    else:

        factor_hora = 1.0

    estado = {

        "clima": clima,
        "hora": hora,
        "tipo_dia": tipo_dia,

        "factor_hora": factor_hora,
        "factor_trafico": factor_hora,
        "trafico_aristas": {},

        "accidentes": {},

        "turno": 0,
        "evento_extremo": False,
        "factor_evento": 1.0,
    }

    return estado

def actualizar_mundo(G, estado, rng, hora):
    estado["turno"] += 1
    """
    Actualiza TODO el mundo dinámico.
    """
    estado["hora"] = hora
    # =====================================================
    # 1. CLIMA (CADENAS DE MARKOV)
    # =====================================================

    estado["clima"] = clima_markov(
        rng,
        estado["clima"]
    )

    

    # =====================================================
    # 2. TIPO DE DÍA (CADENAS DE MARKOV)
    # =====================================================

    estado["tipo_dia"] = tipo_dia_markov(
        rng,
        estado["tipo_dia"]
    )



    # =====================================================
    # 3. FACTOR GLOBAL DEL TRÁFICO
    # =====================================================

    # Base normal/lognormal
    factor_normal = factor_trafico_normal(
        rng,
        mu=1.0,
        sigma=0.10
    )

    factor_lognormal = factor_trafico_lognormal(
        rng,
        mean=0,
        sigma=0.20
    )

    factor_global = factor_normal * factor_lognormal
    #factor por hora del dia
    factor_hora = obtener_factor_hora(hora)

    factor_global *= factor_hora
    estado["factor_trafico"] = factor_global

    # =====================================================
    # 4. EFECTO DEL CLIMA
    # =====================================================

    # 0 = soleado
    # 1 = lluvia
    # 2 = tormenta

    if estado["clima"] == 1:

        factor_global *= 1.3

    elif estado["clima"] == 2:

        factor_global *= 1.8



    # =====================================================
    # 5. EFECTO DEL TIPO DE DÍA
    # =====================================================

    # 0 = buen día
    # 1 = normal
    # 2 = horrible

    if estado["tipo_dia"] == 0:

        lambda_accidentes = 1

    elif estado["tipo_dia"] == 1:

        lambda_accidentes = 3

    else:

        lambda_accidentes = 8

        factor_global *= 1.5



    estado["factor_global"] = factor_global



    # =====================================================
    # 6. DISMINUIR DURACIÓN DE ACCIDENTES
    # =====================================================

    accidentes_a_borrar = []

    for arista in estado["accidentes"]:

        estado["accidentes"][arista] -= 1

        if estado["accidentes"][arista] <= 0:

            accidentes_a_borrar.append(arista)



    for arista in accidentes_a_borrar:

        del estado["accidentes"][arista]



    # =====================================================
    # 7. GENERAR NUEVOS ACCIDENTES (POISSON)
    # =====================================================
    lambda_accidentes *= factor_hora
    cantidad_accidentes = generar_accidentes_poisson(
        rng,
        lambda_accidentes
    )



    edges = list(G.edges())



    for _ in range(cantidad_accidentes):

        arista = random.choice(edges)

        duracion = duracion_accidente_weibull(
            rng,
            alfa=5,
            beta=2
        )

        estado["accidentes"][arista] = duracion



    # =====================================================
    # 8. EVENTOS EXTREMOS (CAUCHY)
    # =====================================================

    caos = evento_extremo_cauchy(
    rng,
    gamma=2
    )

    # ======================================
    # PROBABILIDAD DE EVENTO EXTREMO
    # ======================================

    if caos > 15:

        estado["evento_extremo"] = True

        estado["factor_evento"] = (

            1 + caos * 0.05
        )

    else:

        estado["evento_extremo"] = False

        estado["factor_evento"] = 1.0

    # ======================================
    # APLICAR EFECTO
    # ======================================

    estado["factor_global"] *= (
        estado["factor_evento"]
    )

    # =====================================================
    # 9. CALCULAR FACTORES POR ARISTA
    # =====================================================

    trafico_aristas = {}



    for u, v, k, data in G.edges(keys=True, data=True):

        factor = estado["factor_global"]



        # si hay accidente
        if (u, v) in estado["accidentes"]:

            factor *= 5



        trafico_aristas[(u, v)] = factor



    estado["trafico_aristas"] = trafico_aristas



    return estado