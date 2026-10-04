def leer_grafo(ruta):
    with open(ruta,"r",encoding="utf-8") as fichero:
        nodos, aristas = map(int, fichero.readline().split())
        vecinos=[[] for _ in range(nodos)]
        for linea in fichero:
            nodo1,nodo2=map(int,linea.split())
            vecinos[nodo1].append(nodo2)
            vecinos[nodo2].append(nodo1)
    return nodos,aristas,vecinos
