from simpleai.search import SearchProblem



class RoverProblem(SearchProblem):

    def is_goal(self, state):
        return not state[3] and not state[4]

    def cost(self, state, action, state2):
        pass

    def result(self, state, action):
        pass

    def actions(self, state):
        pass

    def heuristic(self, state):
        pass

def planear_rover(
    rover_inicio,
    bateria_inicial,
    zonas_sombra,
    tuple()muestras_igneas,
    muestras_sedimentarias,
):
#    """Devuelve la lista de acciones para recolectar y depositar todas las muestras."""
    raise NotImplementedError("Pendiente implementar el planificador con SimpleAI.")








