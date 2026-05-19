from simpleai.search import SearchProblem, astar


class RoverProblem(SearchProblem):
    def __init__(self, initial_state, zonas_sombra):
        self.zonas_sombra = tuple(zonas_sombra)
        super().__init__(initial_state)

    def is_goal(self, state):

        posicion, bateria, taladro, ingneas, sedimentarias, carga = state

        # el chat me dio esta forma de hacer un bool y que quede prolijo en el if de abajo !

        noIgneas = len(ingneas) == 0
        noSedimentarias = len(sedimentarias) == 0
        noMasCarga = len(carga) == 0

        if noIgneas and noSedimentarias and noMasCarga:
            return True

        else:
            return False

    def actions(self, state):
        acciones = []

        posicion, bateria, taladro, ingneas, sedimentarias, carga = state
        fila, columna = posicion

        # movimientos basicos

        movimientos = [
            (
                -1,
                0,
            ),  # esto es arriba pq mueve el primer elemento de forma neg oseea q esta restando una fila
            (1, 0),
            (0, -1),  # esti es izq porq al restar una col se mueve a una col anterior
            (0, 1),
        ]

        for df, dc in movimientos:
            nueva_fila = fila + df
            nueva_col = columna + dc

            if bateria - 1 > 0:
                acciones.append(("moverse", (nueva_fila, nueva_col)))

        # sobremarcha

        sobremarcha = [
            (
                -2,
                0,
            ),  # esto es arriba pq mueve el primer elemento de forma neg oseea q esta restando una fila
            (2, 0),
            (0, -2),  # esti es izq porq al restar una col se mueve a una col anterior
            (0, 2),
        ]

        for df, dc in sobremarcha:
            nueva_fila = fila + df
            nueva_col = columna + dc

            if bateria - 4 > 0:
                acciones.append(("sobremarcha", (nueva_fila, nueva_col)))

        # ahora hago equipar los 2 taladros por separado
        # condiciones: equipar si no lo tengo ya y que gasta 1 de bat.
        # tmb pense q pueda equiparlo solo si existen tdv muestras pendientes de ese tipo

        if taladro != "termico" and len(ingneas) > 0 and bateria - 1 > 0:
            acciones.append(("equipar", "termico"))

        if taladro != "percusion" and len(sedimentarias) > 0 and bateria - 1 > 0:
            acciones.append(("equipar", "percusion"))

        # ahora la parte de recoleccion, tiene que:
        # estar parado en una muestra | tener taladro correcto | tener espacio | que la bat le de

        if posicion in ingneas and taladro == "termico" and len(carga) <= 1 and bateria - 3 > 0:
            acciones.append(("recolectar", "ignea"))

        if (
            posicion in sedimentarias
            and taladro == "percusion"
            and len(carga) <= 1
            and bateria - 3 > 0
        ):
            acciones.append(("recolectar", "sedimentaria"))

        # ahora sigue depositar
        # RESTRICCIONES: que tengas 2 cargas arriba o 1 porque ya no quedan mas

        muestras_totales = len(ingneas) + len(sedimentarias)
        if len(carga) > 0 and bateria - 1 > 0:
            if len(carga) == 2 or muestras_totales == 0:
                acciones.append(("depositar", None))

        # ahora la parte de recargar
        # no tiene q estar en zona sombra y que no tenga bat max
        if posicion not in self.zonas_sombra and bateria < 20:
            if bateria <= 4 or len(self.zonas_sombra) > 0:
                acciones.append(("recargar", None))

        return acciones
        pass

    def result(self, state, action):

        posicion, bateria, taladro, igneas, sedimentarias, carga = state
        tipo, parametro_cualq = action

        # si la accion es moverse, cambio posicion y bateria

        if tipo == "moverse":
            nueva_posicion = parametro_cualq
            nueva_bateria = bateria - 1
            return (nueva_posicion, nueva_bateria, taladro, igneas, sedimentarias, carga)

            # si la accion es sobremarcha, lo mismo solo que mas bat y mas posicion
        elif tipo == "sobremarcha":
            nueva_posicion = parametro_cualq
            nueva_bateria = bateria - 4
            return (nueva_posicion, nueva_bateria, taladro, igneas, sedimentarias, carga)

            # si accion es equipar , cambio taladro y bat -1
        elif tipo == "equipar":
            nuevo_taladro = parametro_cualq
            bateria_nueva = bateria - 1
            return (posicion, bateria_nueva, nuevo_taladro, igneas, sedimentarias, carga)

            # para recolectar hay 2 tipos y hay q agregar la carga y sacar de la lista la que agarre
        elif tipo == "recolectar":
            tipo_piedra = parametro_cualq
            baterianueva = bateria - 3

            if tipo_piedra == "ignea":
                nuevas_igneas = tuple(muestra for muestra in igneas if muestra != posicion)
                nueva_carga = carga + ("ignea",)

                return (posicion, baterianueva, taladro, nuevas_igneas, sedimentarias, nueva_carga)

            elif tipo_piedra == "sedimentaria":
                nuevas_sed = tuple(muestra for muestra in sedimentarias if muestra != posicion)
                nueva_carga = carga + ("sedimentaria",)

                return (posicion, baterianueva, taladro, igneas, nuevas_sed, nueva_carga)

            # con depositar hay q restar bat
        elif tipo == "depositar":
            nuevas_bat = bateria - 1
            nueva_carga = ()
            return (posicion, nuevas_bat, taladro, igneas, sedimentarias, nueva_carga)

        elif tipo == "recargar":
            nueva_bateria = bateria + 10

            if nueva_bateria > 20:
                nueva_bateria = 20

            return (posicion, nueva_bateria, taladro, igneas, sedimentarias, carga)

        pass

    def cost(self, state, action, state2):
        if action[0] == "moverse":
            return 1
        elif action[0] == "sobremarcha":
            return 1
        elif action[0] == "equipar":
            return 3
        elif action[0] == "recolectar":
            return 2
        elif action[0] == "depositar":
            return len(state[5])
        elif action[0] == "recargar":
            return 4

    def heuristic(self, state):

        # cada muestra usa minimo 2 min para recolectar
        # las q estan cargadas necesitan 1 min minimo para depositar
        # no cuento movimientos, taladro, recargas, es una heuristica q infraestima pero sirve para guiar la busqueda

        posicion, bateria, taladro, ingneas, sedimentarias, carga = state

        muestras_total = ingneas + sedimentarias

        recolectar_y_depositar = len(muestras_total) * 3

        costo_dep = len(carga)

        if muestras_total:
            fila, col = posicion

            distancia_minima = min(
                abs(fila - mfila) + abs(col - mcol) for mfila, mcol in muestras_total
            )

            costo_moverse_minimo = (distancia_minima + 1) // 2
        else:
            costo_moverse_minimo = 0

        return costo_moverse_minimo + recolectar_y_depositar + costo_dep


def planear_rover(
    rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias
):

    INICIAL_STATE = (
        rover_inicio,  # posicion inicial
        bateria_inicial,  # bat
        None,  # taladro equipado
        tuple(muestras_igneas),  # igneas pendientes
        tuple(muestras_sedimentarias),  # sedimentarias pendientes
        (),  # carga actual
    )

    # crea el problema y le pasa: como empieza el mundo | donde estan las zonas de sombra
    problema = RoverProblem(INICIAL_STATE, zonas_sombra)

    # le dice a simpleai que resuelva con astar
    resultado = astar(problema, graph_search=True)

    acciones = []

    # recorre el camino encontrado
    for accion, estado in resultado.path():
        # el primer paso viene con accion None, pq representa el estado inicial
        if accion is not None:
            acciones.append(accion)

    return acciones
