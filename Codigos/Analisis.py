# ============================================
# Analisis.py
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


# ============================================
# CARGAR
# ============================================

def cargar_resultados(archivo):

    if archivo.endswith(".csv"):

        return pd.read_csv(archivo)

    return pd.read_excel(archivo)


# ============================================
# ERROR RELATIVO
# ============================================

def calcular_error_relativo(df):

    df["error_relativo"] = (

        (
            df["tiempo_real"]
            -
            df["tiempo_fantasma"]
        )

        /

        df["tiempo_fantasma"]
    )

    return df


# ============================================
# RESUMEN ESTADÍSTICO
# ============================================

def generar_resumen_estadistico(resultados):

    df = pd.DataFrame(resultados)

    resumen = {

        "promedio_error_relativo":
            df["error_relativo"].mean(),

        "max_error_relativo":
            df["error_relativo"].max(),

        "promedio_tiempo_real":
            df["tiempo_real"].mean(),

        "promedio_tiempo_fantasma":
            df["tiempo_fantasma"].mean(),

        "promedio_recalculos":
            df["recalculos_real"].mean()
    }

    return resumen


# ============================================
# GUARDAR CSV
# ============================================

def guardar_resultados_csv(
    resultados,
    archivo="resultados.csv"
):

    df = pd.DataFrame(resultados)

    df.to_csv(
        archivo,
        index=False
    )

    print(f"CSV guardado: {archivo}")


# ============================================
# GUARDAR EXCEL
# ============================================

def guardar_resultados_excel(
    resultados,
    archivo="resultados.xlsx"
):

    df = pd.DataFrame(resultados)

    df.to_excel(
        archivo,
        index=False
    )

    print(f"Excel guardado: {archivo}")


# ============================================
# HISTOGRAMA ERROR
# ============================================

def histograma_error(
    df,
    carpeta_salida=None
):

    plt.figure(figsize=(10,6))

    plt.hist(
        df["error_relativo"],
        bins=50
    )

    plt.xlabel("Error relativo")

    plt.ylabel("Frecuencia")

    plt.title(
        "Distribución del error relativo"
    )

    plt.grid(True)

    if carpeta_salida:

        os.makedirs(
            carpeta_salida,
            exist_ok=True
        )

        plt.savefig(
            f"{carpeta_salida}/histograma_error.png",
            dpi=300,
            bbox_inches="tight"
        )

    plt.close()


# ============================================
# HISTOGRAMA TIEMPOS
# ============================================

def histograma_tiempos(
    df,
    carpeta_salida=None
):

    plt.figure(figsize=(10,6))

    plt.hist(
        df["tiempo_real"],
        bins=40,
        alpha=0.7,
        label="Real"
    )

    plt.hist(
        df["tiempo_fantasma"],
        bins=40,
        alpha=0.7,
        label="Fantasma"
    )

    plt.legend()

    plt.grid(True)

    if carpeta_salida:

        os.makedirs(
            carpeta_salida,
            exist_ok=True
        )

        plt.savefig(
            f"{carpeta_salida}/histograma_tiempos.png",
            dpi=300,
            bbox_inches="tight"
        )

    plt.close()


# ============================================
# BOXPLOT
# ============================================

def boxplot_error(
    df,
    carpeta_salida=None
):

    plt.figure(figsize=(8,5))

    plt.boxplot(
        df["error_relativo"]
    )

    plt.title(
        "Boxplot Error Relativo"
    )

    plt.grid(True)

    if carpeta_salida:

        os.makedirs(
            carpeta_salida,
            exist_ok=True
        )

        plt.savefig(
            f"{carpeta_salida}/boxplot_error.png",
            dpi=300,
            bbox_inches="tight"
        )

    plt.close()


# ============================================
# SCATTER ACCIDENTES
# ============================================

def scatter_accidentes_vs_error(
    df,
    carpeta_salida=None
):

    if "cantidad_accidentes" not in df.columns:

        return

    plt.figure(figsize=(10,6))

    plt.scatter(
        df["cantidad_accidentes"],
        df["error_relativo"],
        alpha=0.5
    )

    plt.xlabel(
        "Cantidad accidentes"
    )

    plt.ylabel(
        "Error relativo"
    )

    plt.grid(True)

    if carpeta_salida:

        os.makedirs(
            carpeta_salida,
            exist_ok=True
        )

        plt.savefig(
            f"{carpeta_salida}/scatter_accidentes.png",
            dpi=300,
            bbox_inches="tight"
        )

    plt.close()


# ============================================
# GENERADOR GENERAL
# ============================================

def generar_histogramas(
    resultados,
    carpeta_salida="Graficas"
):

    df = pd.DataFrame(resultados)

    histograma_error(
        df,
        carpeta_salida
    )

    histograma_tiempos(
        df,
        carpeta_salida
    )

    boxplot_error(
        df,
        carpeta_salida
    )

    scatter_accidentes_vs_error(
        df,
        carpeta_salida
    )

    print("Gráficas generadas correctamente")


# ============================================
# ESCENARIOS EXTREMOS
# ============================================

def rutas_extremas(df):

    peor = df.loc[
        df["error_relativo"].idxmax()
    ]

    mejor = df.loc[
        df["error_relativo"].idxmin()
    ]

    print("\nPEOR ESCENARIO")
    print(peor)

    print("\nMEJOR ESCENARIO")
    print(mejor)


# ============================================
# ANÁLISIS CLIMA
# ============================================

def analizar_por_clima(df):

    if "clima" not in df.columns:

        return

    grupos = df.groupby("clima")

    for clima, grupo in grupos:

        print()
        print("CLIMA:", clima)

        print(
            grupo["error_relativo"].mean()
        )


# ============================================
# FRACASOS
# ============================================

def analizar_fracasos(df):

    fracasos = df[
        df["error_relativo"] > 0.5
    ]

    probabilidad = (
        len(fracasos)
        /
        len(df)
    )

    print(
        "Probabilidad fracaso:",
        probabilidad
    )

    return fracasos