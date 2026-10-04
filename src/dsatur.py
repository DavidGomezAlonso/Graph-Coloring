def menor_color_disponible(lista):
        n=1
        while n in lista:
            n+=1
        return n

def dsatur_greedy(vecinos) :
    nodos=len(vecinos)
    saturacion=[0]*nodos
    grados=[]
    for nodo in vecinos:
        grados.append(len(nodo))
    colores=[0]*nodos   # Coloracion final
    colores_vecinos=[set() for _ in range(nodos)]     
    # ---------------------------------------------------------
    # Asignacion inicial
    # ---------------------------------------------------------
    indice=grados.index(max(grados))
    colores[indice]=1
    # ---------------------------------------------------------
    # Actualizacion saturacion
    # ---------------------------------------------------------    
    for i in vecinos[indice]:
        colores_vecinos[i].add(1)
        saturacion[i]+=1
    disponibles=list(range(nodos))
    disponibles.remove(indice)
    # ---------------------------------------------------------
    # Ejecucion algoritmo DSATUR GREEDY
    # ---------------------------------------------------------
    for _ in range(nodos-1):
        indice=max(disponibles, key= lambda p: (saturacion[p],grados[p]))
        color_nuevo=menor_color_disponible(colores_vecinos[indice])
        colores[indice]=color_nuevo
        disponibles.remove(indice)
        for i in vecinos[indice]:
            colores_vecinos[i].add(color_nuevo)
            saturacion[i]=len(colores_vecinos[i]) 
    return colores


    



    


