# Conductores.py

class Conductor:

    def __init__(
        self,
        origen,
        destino,
        fantasma=False
    ):

        # ==================================================
        # IDENTIDAD
        # ==================================================

        self.fantasma = fantasma

        self.origen = origen
        self.destino = destino

        self.nodo_actual = origen



        # ==================================================
        # MOVIMIENTO
        # ==================================================

        self.ruta_actual = []

        self.arista_actual = None

        self.progreso_arista = 0.0

        # 0.0 -> acaba de entrar
        # 0.5 -> mitad
        # 1.0 -> salió



        # ==================================================
        # ESTADO
        # ==================================================

        self.llego = False



        # ==================================================
        # MÉTRICAS
        # ==================================================

        self.tiempo_total = 0.0

        self.distancia_total = 0.0

        self.recalculos = 0

        self.historial_nodos = [origen]



    # ======================================================
    # ACTUALIZAR RUTA
    # ======================================================

    def actualizar_ruta(self, ruta):

        if ruta is None:
            return

        if len(ruta) < 2:
            return

        self.ruta_actual = ruta.copy()

        self.recalculos += 1
        # =====================================
        # SI YA ESTÁ EN UNA CALLE
        # =====================================

        if self.arista_actual is not None:

            u, v = self.arista_actual

            # mantener calle actual
            self.ruta_actual = [u] + ruta

        else:

            self.ruta_actual = ruta.copy()

        self.recalculos += 1


    # ======================================================
    # MOVER CONDUCTOR
    # ======================================================

    def mover(
        self,
        duracion_turno,
        G,
        estado,
        funcion_peso
    ):

        # ----------------------------------------------
        # Si ya llegó no hacer nada
        # ----------------------------------------------

        if self.llego:
            return



        # ----------------------------------------------
        # Sumar tiempo total
        # ----------------------------------------------

        self.tiempo_total += duracion_turno



        # ----------------------------------------------
        # Si no hay ruta válida
        # ----------------------------------------------

        if len(self.ruta_actual) < 2:

            self.llego = True

            return



        # ----------------------------------------------
        # Si no está actualmente en una calle,
        # tomar la siguiente arista
        # ----------------------------------------------

        if self.arista_actual is None:

            u = self.ruta_actual[0]

            v = self.ruta_actual[1]

            self.arista_actual = (u, v)

            self.progreso_arista = 0.0



        # ----------------------------------------------
        # Calle actual
        # ----------------------------------------------

        u, v = self.arista_actual

        data = G[u][v][0]



        # ----------------------------------------------
        # Tiempo dinámico de la calle
        # ----------------------------------------------

        tiempo_calle = funcion_peso(
            u,
            v,
            data,
            estado
        )



        # Evitar división por cero
        if tiempo_calle <= 0:

            tiempo_calle = 0.0001



        # ----------------------------------------------
        # Avance porcentual
        # ----------------------------------------------

        avance = duracion_turno / tiempo_calle



        self.progreso_arista += avance



        # ----------------------------------------------
        # Distancia recorrida
        # ----------------------------------------------

        distancia_avanzada = (
            data["length"]
            * min(avance, 1.0)
        )

        self.distancia_total += distancia_avanzada



        # ----------------------------------------------
        # ¿Terminó la calle?
        # ----------------------------------------------

        if self.progreso_arista >= 1.0:

            self.nodo_actual = v

            self.historial_nodos.append(v)

            self.ruta_actual.pop(0)

            self.arista_actual = None

            self.progreso_arista = 0.0

            if v == self.destino:

                self.llego = True

            # Reiniciar calle
            self.arista_actual = None

            self.progreso_arista = 0.0



            # ------------------------------------------
            # ¿Llegó al destino?
            # ------------------------------------------

            if v == self.destino:

                self.llego = True