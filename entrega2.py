from simpleai.search import CspProblem, backtrack
import itertools
# habs=2
# generators=1
#labs= 2
#etc
def createVariable(habs, generators, labs, deposits, airlocks):
    variables = [] 

    for i in habs: #i=2
        variables.append(f"habs{i}")
    for i in generators: #i=1
        variables.append(f"gen{i}")
    for i in labs: #labs = 2
        variables.append(f"labs{i}")
    for i in deposits:
        variables.append(f"dep{i}")
    for i in airlocks:
        variables.append(f"air{i}")
 

    return variables

#Esta funcion me sirve para saber si la celda esta en el borde
def celda_en_borde(celda, camp_size ):

    fila, columna = celda
    filas, columnas =  camp_size

    #aca devuelvo solo las filas o las columnas que estan en el borde 
    return fila == 0 or columna == 0 or fila == filas - 1 or columna == columnas - 1

def dominios (variables, camp_size, crateres):

    filas, columnas= camp_size

    crateres_set = set(crateres)

    celdasLibres = []

    for fila in range(filas):
        for columna in range(columnas):
            
            celda = fila,columna

            if (celda) not in crateres_set:
                celdasLibres.append(celda)
            
            dominios = []

    for var in variables:

        if var.startswith("air"):    
            dominios[var] = [
                celda for celda in celdasLibres
            if celda_en_borde(celda, camp_size)
            ]

        elif var.startswith("hab"):
            dominios[var] = [
                celda for celda in celdasLibres
                if not celda_en_borde(celda, camp_size)
            ]
        else:
             dominios[var] = celdasLibres
    return dominios  

def no_superpone(variables, valores):
    return valores[0] != valores [1]

def restrcciones(variables):
    constraints = []

    for var1, var2 in itertools.combinations(variables, 2):
        constraints.append(((var1,var2), no_superpone))

    return constraints

