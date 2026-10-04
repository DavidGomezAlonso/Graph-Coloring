def guardar_mejor_coloracion(solucion, archivo="coloracion.txt"):
    if len(solucion) == 0:
        raise ValueError("La solucion no puede estar vacia")
    num_colores = max(solucion) + 1

    try:
        with open(archivo, "r") as fichero:
            primera_linea = fichero.readline().strip()

            if primera_linea:
                mejor_num_colores = int(primera_linea)
            else:
                mejor_num_colores = float("inf")

    except FileNotFoundError:
        
        mejor_num_colores = float("inf")

    # ---------------------------------------------------------
    # Sobrescribir 
    # ---------------------------------------------------------
    if num_colores < mejor_num_colores:

        with open(archivo, "w") as fichero:

            # Primera linea: numero de colores
            fichero.write(str(num_colores) + "\n")

            # Segunda linea: color de cada vertice
            fichero.write(" ".join(map(str, solucion)) + "\n")

        print("Nueva mejor coloracion guardada:",num_colores,"colores")

        return True

    print("La coloracion no mejora la almacenada.","Actual:", num_colores,"Mejor:", mejor_num_colores)

    return False