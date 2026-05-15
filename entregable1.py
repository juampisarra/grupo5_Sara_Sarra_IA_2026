from simpleai.search import SearchProblem, astar

class RoverProblem(SearchProblem):

    def is_goal(self, state):
        pass
    
    def actions(self, state):
        pass
    def result(self, state, action):
        pass
    def cost(self, state1, action, state2):
        pass
    def heuristic(self, state):
        pass
    
def planear_rover (rover_inicio, bateria_inicial, zonas_sombra, muestras_igneas, muestras_sedimentarias):
    INICIAL_STATE = (
        rover_inicio,                    # posición
        bateria_inicial,                 # batería
        None,                            # taladro equipado
        tuple(muestras_igneas),          # muestras ígneas pendientes
        tuple(muestras_sedimentarias),   # muestras sedimentarias pendientes
        0,                               # carga actual
    )