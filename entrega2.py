from simpleai.search import CspProblem, backtrack
import itertools

# habs=2
# generators=1
#labs= 2
#etc
def createVariable(habs, generators, labs, deposits, airlocks):
    variables = [] 

    for i in range(habs): #i=2
        variables.append(f"habs{i}")
    for i in range(generators): #i=1
        variables.append(f"gen{i}")
    for i in range(labs): #labs = 2
        variables.append(f"labs{i}")
    for i in range(deposits):
        variables.append(f"dep{i}")
    for i in range(airlocks):
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
            
    #se usa como diccionario
    dominios = {}

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

def son_adyacentes(celda1, celda2):
    
    fila1, columna1 = celda1
    fila2, columna2 = celda2

    return abs(fila1 - fila2) + abs(columna1 - columna2) == 1

def celdas_adyacentes(celda, camp_size):

    
    fila, columna = celda
    filas, columnas = camp_size

    adyacentes = [
        (fila - 1, columna),
        (fila + 1, columna),
        (fila, columna + 1),
        (fila, columna - 1),
    ]

    return [
        celda for celda in adyacentes
        if 0 <= celda[0] < filas and 0 <= celda[1] < columnas
    ]


def no_son_adyacente(variables, valores):
    return not son_adyacentes(valores[0], valores[1])

def lab_adyacente_deposito(variables, valores):
    celda_laboratorio = valores[0]

    #valores[1:] devuelve una lista/tupla de celda. Ej:
    #((2, 3), (4, 1), (1, 5))
    depositos = valores[1:]

    return any(son_adyacentes(celda_laboratorio,deposito) for deposito in depositos)

def restrcciones(variables, camp_size, crateres):
    constraints = []

    #No genera pares repetidos, (0,1) (1,0)
    for var1, var2 in itertools.combinations(variables, 2):
        constraints.append(((var1,var2), no_superpone))

        if ( 
            var1.startswith("gen") and var2.startswith("hab")
        ) or (
            var1.startswith("hab") and var2.startswith("gen")
        ): constraints.append(((var1,var2), no_son_adyacente))

        if (var1.startswith("gen") and var2.startswith("gen")
        ): constraints.append(((var1,var2), no_son_adyacente))

    habitacionales = [var for var in variables if var.startswith("habs")]
    for habitacional in habitacionales:
        variablesX = [var for var in variables if var !=  habitacional]
        constraints.append(
            ((habitacional, *variablesX), hab_tiene_celdas_libre(camp_size, crateres))
        )

    
    #el primer var es lo que devuelve, es decir
    #nuevo_elemento for elemento in lista if condicion
    depositos = [var for var in variables if var.startswith("dep")]
    laboratorios = [var for var in variables if var.startswith("labs")]

    for laboratorio in laboratorios:
        constraints.append(((laboratorio, *depositos), lab_adyacente_deposito))



    return constraints

def hab_tiene_celdas_libre(camp_size, crateres):
    crateres_set = set(crateres)

    def restriccion(variables, valores):
        celda_hab = valores[0]
        celdas_ocupadas = set(valores)

        for celda in celdas_adyacentes(celda_hab, camp_size):
            if celda not in crateres_set and celda not in celdas_ocupadas:
                return True
            
        return False
    
    return restriccion
