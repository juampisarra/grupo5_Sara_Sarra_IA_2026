from simpleai.search import SearchProblem, astar

class RoverProblem(SearchProblem):

    def is_goal(self, state):
        pass
    
    def actions(self, state):
        pass
    def result(self, state, action):
        pass
    def cost(self, state, action, state2):
        if action[0] == "moverse":
            return 1
        else if action[0] == "sobremarcha":
            return 1    
        else if action[0] == "equipar":
            return 3
        else if action[0] == "recolectar":
            return 2
        else if action[0] == "depositar":
            return len(state[5])
        else if action[0] == "recargar":
            return 4

    def heuristic(self, state):
        pass
    
def planear_rover (rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    INICIAL_STATE = (
        rover_inicio,                    # posición
        bateria_inicial,                 # batería
        None,                            # taladro equipado
        tuple(muestras_igneas),          # muestras ígneas pendientes
        tuple(muestras_sedimentarias),   # muestras sedimentarias pendientes
        (),                              # carga actual
    )

    constante_sombras = zonas_sombra
