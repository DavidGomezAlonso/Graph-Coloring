import random
import numpy as np
from numba import njit
def list_to_CSR(vecinos):
    n = len(vecinos)
    
    offsets=np.empty(n+1,dtype=np.int32)
    offsets[0]=0
    total=0
    for i,valores in enumerate(vecinos):
        total+=len(valores)
        offsets[i+1]=total
    adyacentes=np.empty(total,dtype=np.int32)
    
    for i,vecino in enumerate(vecinos):
        adyacentes[offsets[i]:offsets[i+1]]=vecino


        
    return offsets,adyacentes




def normalizar_colores(colores):
    usados=sorted(set(colores))
    conversion={}
    for i,color in enumerate(usados):
        conversion[color]=i
    for i,color in enumerate(colores):
        colores[i]=conversion[color]
    return colores
def contar_conflictos(vecinos,colores):
    conflictos=0
    for vertice,color in enumerate(colores):
        for vecino in vecinos[vertice]:
            if vecino>vertice and colores[vecino]==color:
                conflictos+=1
    return conflictos
def coloracion_valida(vecinos,colores):
    return contar_conflictos(vecinos,colores)==0
def crear_inicial(colores,k,rng):
    nueva=[]
    for color in colores:
        if color<k:
            nueva.append(color)
        else:
            nueva.append(rng.randrange(k))
    return nueva
@njit(cache=True)
def tabuCol(ady,offsets,k,colores,max_iter=100000,seed=12345):
    nodos=len(colores)
    np.random.seed(seed)

    
    # ---------------------------------------------------------------
    # 2. MATRIZ GAMMA
    # ---------------------------------------------------------------   
    
    gamma=np.zeros((nodos,k),dtype=np.int32)
    for vertice in range(nodos):
        inicio=offsets[vertice]
        fin=offsets[vertice+1]
        for p in range(inicio,fin):
            vecino=ady[p]

            gamma[vertice,colores[vecino]]+=1
    # ----------------------------------------------------------
    # 3. CONFLICTOS INICIALES
    # ----------------------------------------------------------
    conflictos=0
    for vertice in range(nodos):
        conflictos+=gamma[vertice,colores[vertice]]
    conflictos//=2
    if conflictos==0:
        return colores,0,0
    mejor_colores=colores.copy()
    mejor_conflictos=conflictos
    # ----------------------------------------------------------
    # 4. LISTA TABU
    # ----------------------------------------------------------
    
    tabu=np.zeros((nodos,k),dtype=np.int64)
    ultima_iteracion=0
    # ----------------------------------------------------------
    # 4. BUSQUEDA TABU
    # ----------------------------------------------------------
    for iteracion in range(1,max_iter+1):
        ultima_iteracion=iteracion
        mejor_delta=1000000000
        mejor_vertice=-1
        mejor_color=-1
        num_vertices_conflictivos=0
        num_empates=0
        # ------------------------------------------------------
        # Buscar el mejor movimiento
        # ------------------------------------------------------  
        for vertice in range(nodos):
            color_actual=colores[vertice]
            conflictos_vertice=gamma[vertice,color_actual]
            if conflictos_vertice==0:
                continue
            num_vertices_conflictivos+=1
            for color_nuevo in range(k):
                if color_nuevo==color_actual:
                    continue
                delta=gamma[vertice,color_nuevo]-gamma[vertice,color_actual]
                nuevos_conflictos=conflictos+delta
                # ------------------------------------------------------
                # Comprobacion TABU
                # ------------------------------------------------------
                es_tabu=tabu[vertice,color_nuevo]>iteracion
                # ------------------------------------------------------
                # Criterio aspiracion
                # ------------------------------------------------------
                if es_tabu and nuevos_conflictos>=mejor_conflictos:
                    continue
                # ------------------------------------------------------
                # Guarda mejor movimiento
                # ------------------------------------------------------
                if delta<mejor_delta:
                    mejor_delta=delta
                    mejor_vertice=vertice
                    mejor_color=color_nuevo
                    num_empates=1
                elif delta==mejor_delta:
                    num_empates+=1
                    if np.random.randint(num_empates)==0:
                        mejor_vertice=vertice
                        mejor_color=color_nuevo
        if mejor_vertice==-1:
            break
        # ------------------------------------------------------
        # Realizamos movimiento
        # ------------------------------------------------------
        vertice=mejor_vertice
        color_nuevo=mejor_color
        color_anterior=colores[vertice]
        delta=gamma[vertice,color_nuevo]-gamma[vertice,color_anterior]
        # ------------------------------------------------------
        # Cambiamos color
        # ------------------------------------------------------
        colores[vertice]=color_nuevo
        conflictos+=delta
        # ------------------------------------------------------
        # Tabu tenure
        # ------------------------------------------------------
        tenure=3*num_vertices_conflictivos//5+np.random.randint(10)
        tabu[vertice,color_anterior]=iteracion+tenure
        # ------------------------------------------------------
        # Actualizar gamma
        # ------------------------------------------------------
        inicio=offsets[vertice]
        fin=offsets[vertice+1]
        for p in range(inicio,fin):
            vecino=ady[p]
            gamma[vecino,color_anterior]-=1
            gamma[vecino,color_nuevo]+=1
        # ------------------------------------------------------
        # Nueva mejor solucion
        # ------------------------------------------------------
        if conflictos<mejor_conflictos:
            mejor_conflictos=conflictos
            mejor_colores[:]=colores
            if mejor_conflictos==0:
                return (mejor_colores,0,iteracion)
    return(mejor_colores,mejor_conflictos,ultima_iteracion)

def optimo_tabu_col(vecinos,colores,max_iter_intento=100000,reintentos=3,seed=12345,narra=False):
    rng=random.Random(seed)
    colores=normalizar_colores(colores)
    offsets,ady=list_to_CSR(vecinos)
    mejor = colores
    num_colores=max(colores)+1
    while num_colores>1:
        num_objetivo=num_colores-1
        if narra:
            print("Probando TabuCol con",num_objetivo,"colores")
        solucion_k=None
        mejor_num_conflictos=float("inf")
        for intento in range(1,reintentos+1):
            inicial=crear_inicial(mejor,num_objetivo,rng)
            inicial=np.asarray(inicial,dtype=np.int32)
            solucion,conflictos,iteraciones=tabuCol(ady,offsets,num_objetivo,inicial,max_iter_intento,rng.randrange(10**9))
            mejor_num_conflictos=min(mejor_num_conflictos,conflictos)
            if narra:
                print("Intento",intento,"->",conflictos,"conflictos en",iteraciones,"iteraciones")
            if conflictos==0:
                solucion_k=normalizar_colores(solucion)
                break
        if solucion_k is None:
            if narra:
                print("\nNo se encontro solucion con",num_objetivo,"colores")
                print("Mejor intento",mejor_num_conflictos,"conflictos")
            break
        mejor=solucion_k
        num_colores=max(mejor)+1
        if narra:
            print("Exito",num_colores,"colores")
    
    return mejor
    


        
        
        