# Distribuciones_probabilidad.py

import math
import numpy as np


def generar_accidentes_poisson(rng, lam):

    """
    lam:
        promedio esperado de accidentes
    """

    return rng.poisson(lam=lam)
def factor_trafico_normal(rng, mu=1.0, sigma=0.15):

    """
    Devuelve un multiplicador de tráfico.

    Ejemplo:
        1.0 = normal
        1.2 = 20% más lento
        0.8 = más rápido
    """

    x = rng.normal(mu, sigma)

    return max(x, 0.1)
def factor_trafico_lognormal(
    rng,
    mean=0,
    sigma=0.25
):

    """
    Multiplicador realista de tráfico.
    """

    return rng.lognormal(
        mean=mean,
        sigma=sigma
    )
def duracion_accidente_weibull(
    rng,
    alfa=5,
    beta=2
):

    """
    alfa:
        escala

    beta:
        forma
    """

    y = rng.uniform(0,1)

    x = alfa * (
        (-math.log(1-y)) ** (1/beta)
    )

    return x
def evento_extremo_cauchy(
    rng,
    x0=0,
    gamma=5
):

    y = rng.uniform(0,1)

    x = x0 + gamma * math.tan(
        math.pi * (y - 0.5)
    )

    return abs(x)
def tiempo_exponencial(
    rng,
    escala=1.0
):

    return rng.exponential(scale=escala)

# 0 = soleado
# 1 = lluvia
# 2 = tormenta
def clima_markov(rng, estado_actual):

    matriz = [

        [0.80, 0.18, 0.02],

        [0.30, 0.50, 0.20],

        [0.10, 0.40, 0.50]
    ]

    probabilidades = matriz[estado_actual]

    nuevo_estado = rng.choice(
        [0,1,2],
        p=probabilidades
    )

    return nuevo_estado
def reaccion_conductor(rng):

    """
    Tiempo que tarda en reaccionar
    al nuevo camino.

    Distribución exponencial:
    la mayoría reacciona rápido,
    algunos MUY lento.
    """

    return rng.exponential(scale=2.0)
# 0 = buen día
# 1 = día normal
# 2 = día horrible

def tipo_dia_markov(rng, estado_actual):

    matriz = [

        [0.70, 0.25, 0.05],

        [0.20, 0.60, 0.20],

        [0.10, 0.30, 0.60]
    ]

    probabilidades = matriz[estado_actual]

    return rng.choice(
        [0,1,2],
        p=probabilidades
    )