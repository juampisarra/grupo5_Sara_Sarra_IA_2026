"""Solucion generada con asistencia de IA para el problema Ares-1.

La formulacion usa busqueda A* de SimpleAI. El estado es totalmente inmutable
para que graph_search pueda detectar repetidos:

    (posicion, bateria, taladro, igneas_pendientes, sedimentarias_pendientes, carga)

La carga guarda tipos de muestra, porque el costo de depositar depende solo de
cuantas muestras lleva el rover, no de sus coordenadas originales.
"""

from math import ceil

from simpleai.search import SearchProblem, astar


BATERIA_MAXIMA = 20
CARGA_MAXIMA = 2

TALADRO_IGNEA = "termico"
TALADRO_SEDIMENTARIA = "percusion"

MOVIMIENTOS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _distancia_manhattan(origen, destino):
    return abs(origen[0] - destino[0]) + abs(origen[1] - destino[1])


def _minutos_minimos_movimiento(origen, destino):
    """Minimo tiempo de traslado ignorando bateria.

    Como la sobremarcha avanza 2 celdas en 1 minuto y moverse avanza 1 celda en
    1 minuto, para una distancia Manhattan d el menor tiempo posible es ceil(d/2).
    Es una relajacion admisible porque ignora el consumo de bateria.
    """

    return ceil(_distancia_manhattan(origen, destino) / 2)


def _normalizar_muestras(muestras):
    return tuple(sorted(tuple(muestra) for muestra in muestras))


class RoverProblem(SearchProblem):
    def __init__(
        self,
        initial_state,
        zonas_sombra,
        muestras_igneas,
        muestras_sedimentarias,
    ):
        self.zonas_sombra = frozenset(zonas_sombra)
        self.todas_las_muestras = tuple(muestras_igneas) + tuple(muestras_sedimentarias)
        self.limites = self._calcular_limites(initial_state[0], zonas_sombra)
        super().__init__(initial_state)

    def _calcular_limites(self, rover_inicio, zonas_sombra):
        """Acota la grilla infinita a una region suficiente para los escenarios.

        No existen obstaculos: las sombras solo afectan la recarga. Por eso nunca
        hace falta alejarse demasiado del rectangulo que contiene inicio, muestras
        y sombras relevantes; el margen permite encontrar celdas soleadas vecinas
        incluso si el rectangulo principal esta cubierto por sombra.
        """

        puntos = [rover_inicio, *self.todas_las_muestras, *zonas_sombra]
        filas = [p[0] for p in puntos]
        columnas = [p[1] for p in puntos]

        # Margen generoso pero finito: cubre desvios para recargar fuera de una
        # zona sombreada grande sin volver explosiva la busqueda.
        margen = 4
        return (
            min(filas) - margen,
            max(filas) + margen,
            min(columnas) - margen,
            max(columnas) + margen,
        )

    def _en_limites(self, posicion):
        fila_min, fila_max, col_min, col_max = self.limites
        fila, col = posicion
        return fila_min <= fila <= fila_max and col_min <= col <= col_max

    def _mst_movimiento_minimo(self, posicion, pendientes):
        """Cota inferior del traslado necesario para visitar todas las muestras.

        Cualquier recorrido que parte desde la posicion actual y visita todas las
        muestras pendientes contiene implicitamente un arbol que conecta esos
        puntos. El costo del arbol de expansion minima con distancias relajadas
        por sobremarcha es, por lo tanto, admisible.
        """

        puntos = (posicion, *pendientes)
        if len(puntos) <= 1:
            return 0

        visitados = {puntos[0]}
        no_visitados = set(puntos[1:])
        costo_total = 0

        while no_visitados:
            costo_arista, siguiente = min(
                (
                    _minutos_minimos_movimiento(origen, destino),
                    destino,
                )
                for origen in visitados
                for destino in no_visitados
            )
            costo_total += costo_arista
            visitados.add(siguiente)
            no_visitados.remove(siguiente)

        return costo_total

    def is_goal(self, state):
        _posicion, _bateria, _taladro, igneas, sedimentarias, carga = state
        return not igneas and not sedimentarias and not carga

    def actions(self, state):
        posicion, bateria, taladro, igneas, sedimentarias, carga = state
        fila, col = posicion
        acciones = []

        if bateria > 1:
            for df, dc in MOVIMIENTOS:
                destino = (fila + df, col + dc)
                if self._en_limites(destino):
                    acciones.append(("moverse", destino))

        if bateria > 4:
            for df, dc in MOVIMIENTOS:
                destino = (fila + 2 * df, col + 2 * dc)
                if self._en_limites(destino):
                    acciones.append(("sobremarcha", destino))

        if bateria > 1:
            if igneas and taladro != TALADRO_IGNEA:
                acciones.append(("equipar", TALADRO_IGNEA))
            if sedimentarias and taladro != TALADRO_SEDIMENTARIA:
                acciones.append(("equipar", TALADRO_SEDIMENTARIA))

        if len(carga) < CARGA_MAXIMA and bateria > 3:
            if posicion in igneas and taladro == TALADRO_IGNEA:
                acciones.append(("recolectar", "ignea"))
            if posicion in sedimentarias and taladro == TALADRO_SEDIMENTARIA:
                acciones.append(("recolectar", "sedimentaria"))

        muestras_pendientes = len(igneas) + len(sedimentarias)
        if carga and bateria > 1 and (len(carga) == CARGA_MAXIMA or muestras_pendientes == 0):
            acciones.append(("depositar", None))

        if posicion not in self.zonas_sombra and bateria < BATERIA_MAXIMA:
            acciones.append(("recargar", None))

        return acciones

    def result(self, state, action):
        posicion, bateria, taladro, igneas, sedimentarias, carga = state
        tipo, parametro = action

        if tipo == "moverse":
            return (parametro, bateria - 1, taladro, igneas, sedimentarias, carga)

        if tipo == "sobremarcha":
            return (parametro, bateria - 4, taladro, igneas, sedimentarias, carga)

        if tipo == "equipar":
            return (posicion, bateria - 1, parametro, igneas, sedimentarias, carga)

        if tipo == "recolectar":
            if parametro == "ignea":
                nuevas_igneas = tuple(muestra for muestra in igneas if muestra != posicion)
                return (
                    posicion,
                    bateria - 3,
                    taladro,
                    nuevas_igneas,
                    sedimentarias,
                    carga + ("ignea",),
                )

            nuevas_sedimentarias = tuple(
                muestra for muestra in sedimentarias if muestra != posicion
            )
            return (
                posicion,
                bateria - 3,
                taladro,
                igneas,
                nuevas_sedimentarias,
                carga + ("sedimentaria",),
            )

        if tipo == "depositar":
            return (posicion, bateria - 1, taladro, igneas, sedimentarias, ())

        if tipo == "recargar":
            return (
                posicion,
                min(BATERIA_MAXIMA, bateria + 10),
                taladro,
                igneas,
                sedimentarias,
                carga,
            )

        raise ValueError(f"Accion desconocida: {action!r}")

    def cost(self, state, action, state2):
        tipo = action[0]
        if tipo in ("moverse", "sobremarcha"):
            return 1
        if tipo == "equipar":
            return 3
        if tipo == "recolectar":
            return 2
        if tipo == "depositar":
            return len(state[5])
        if tipo == "recargar":
            return 4
        raise ValueError(f"Accion desconocida: {action!r}")

    def heuristic(self, state):
        posicion, _bateria, taladro, igneas, sedimentarias, carga = state
        pendientes = tuple(igneas) + tuple(sedimentarias)

        if not pendientes:
            return len(carga)

        # Costo inevitable de recolectar cada muestra pendiente y depositar todas
        # las muestras que todavia no estan depositadas.
        h = 2 * len(pendientes) + len(pendientes) + len(carga)

        h += self._mst_movimiento_minimo(posicion, pendientes)

        # Cota inferior de cambios de taladro: cuenta los tipos pendientes y
        # descuenta el tipo que ya esta equipado si sirve para alguna muestra.
        tipos_necesarios = set()
        if igneas:
            tipos_necesarios.add(TALADRO_IGNEA)
        if sedimentarias:
            tipos_necesarios.add(TALADRO_SEDIMENTARIA)
        cambios_minimos = len(tipos_necesarios)
        if taladro in tipos_necesarios:
            cambios_minimos -= 1
        h += 3 * cambios_minimos

        return h


def planear_rover(
    rover_inicio,
    bateria_inicial,
    zonas_sombra,
    muestras_igneas,
    muestras_sedimentarias,
):
    """Devuelve una secuencia optima de acciones para recolectar y depositar todo."""

    igneas = _normalizar_muestras(muestras_igneas)
    sedimentarias = _normalizar_muestras(muestras_sedimentarias)

    initial_state = (
        tuple(rover_inicio),
        bateria_inicial,
        None,
        igneas,
        sedimentarias,
        (),
    )
    problema = RoverProblem(
        initial_state=initial_state,
        zonas_sombra={tuple(pos) for pos in zonas_sombra},
        muestras_igneas=igneas,
        muestras_sedimentarias=sedimentarias,
    )

    resultado = astar(problema, graph_search=True)
    if resultado is None:
        raise RuntimeError("No se encontro solucion, aunque la consigna indica que existe.")

    return [accion for accion, _estado in resultado.path() if accion is not None]
