import gurobipy as gp
from gurobipy import GRB

def colorear_grafo_gurobi(vecinos,numero,coloracion_inicial=[],tiempo_max=None):
    n = len(vecinos)

    if n == 0: 
        return [], 0
    vertices = range(n)
    # ============================================================
    # Construir conjunto de aristas
    # ============================================================
    aristas = set()
    for u in vertices:
        for v in vecinos[u]:

            if v < 0 or v >= n:
                raise ValueError(f"El vertice {u} tiene como vecino a {v}, que está fuera del rango válido.")
            if u == v:
                raise ValueError(f"El vertice {u} tiene un bucle consigo mismo. El grafo no admite una coloracion propia.")
            aristas.add((min(u, v), max(u, v)))

    # ============================================================
    # Procesar coloracion inicial
    # ============================================================
    usar_inicial = len(coloracion_inicial) > 0
    if usar_inicial:
        if len(coloracion_inicial) != n:
            raise ValueError(f"La coloracion inicial debe tener {n} elementos, "f"pero tiene {len(coloracion_inicial)}.")      
        mapa_colores = {}
        coloracion_normalizada = []
        siguiente_color = 0
        for color in coloracion_inicial:
            if color < 0:
                raise ValueError("Los colores de la coloracion inicial deben ser no negativos.")
            if color not in mapa_colores:
                mapa_colores[color] = siguiente_color
                siguiente_color += 1
            coloracion_normalizada.append(mapa_colores[color])
        # Número de colores usados por la solucion inicial
        k = siguiente_color
        # --------------------------------------------------------
        # Comprobar que la solucion inicial es factible
        # --------------------------------------------------------
        for u, v in aristas:
            if (coloracion_normalizada[u]== coloracion_normalizada[v]):
                raise ValueError("La coloracion inicial no es factible: "f"los vertices {u} y {v} son vecinos "f"y tienen el color "f"{coloracion_normalizada[u]}.")
    else:
        # Sin información inicial, el máximo trivial son n colores
        k = n
        coloracion_normalizada = None
    colores = range(k)
    with gp.Env(empty=True) as env:
        env.setParam("OutputFlag", 0)
        env.start()
        # ========================================================
        # Crear modelo
        # ========================================================
        with gp.Model("coloracion_grafos", env=env) as modelo:
            # ----------------------------------------------------
            # Variables
            # ----------------------------------------------------
            # x[v,c] = 1 si el vertice v tiene el color c
            x = modelo.addVars(n,k,vtype=GRB.BINARY,name="x")
            # y[c] = 1 si el color c es utilizado
            y = modelo.addVars(k,vtype=GRB.BINARY,name="y")
            # El primer vertice utiliza el color 0.
            modelo.addConstr(x[0, 0] == 1,name="primer_vertice_color_0")
            # Un vertice v nunca necesita utilizar un color > v.
            for v in vertices:
                for c in range(v + 1, k):
                    x[v, c].UB = 0
            # Los colores se utilizan consecutivamente:
            #
            # y[0] >= y[1] >= y[2] >= ...
            modelo.addConstrs((y[c] >= y[c + 1] for c in range(k - 1)),name="orden_colores")
            # ====================================================
            # Función objetivo
            # ====================================================
            modelo.setObjective(gp.quicksum(y[c] for c in colores),GRB.MINIMIZE)
            # ====================================================
            # Restricción 1
            #
            # Cada vertice debe recibir exactamente un color
            # ====================================================
            modelo.addConstrs((gp.quicksum(x[v, c]for c in colores) == 1 for v in vertices),name="un_color")
            # ====================================================
            # Restricción 2
            #
            # Dos vecinos no pueden tener el mismo color
            # ====================================================
            modelo.addConstrs((x[u, c] + x[v, c] <= 1 for u, v in aristas for c in colores),name="vecinos")
            # ====================================================
            # Restricción 3
            #
            # Si un vertice usa c, entonces el color c está activo
            # ====================================================
            modelo.addConstrs((x[v, c] <= y[c] for v in vertices for c in colores),name="color_usado")
            # ====================================================
            # MIP START
            #
            # Proporcionar la solucion inicial a Gurobi
            # ====================================================
            if usar_inicial:
                for v in vertices:
                    color_v = coloracion_normalizada[v]
                    for c in colores:

                        if c == color_v:
                            x[v, c].Start = 1
                        else:
                            x[v, c].Start = 0
                for c in colores:
                    y[c].Start = 1
            # ====================================================
            # Límite de tiempo
            # ====================================================
            if tiempo_max is not None:
                modelo.Params.TimeLimit = tiempo_max
            # ====================================================
            # CALLBACK
            #
            # Detectar cuándo aparece una solucion con
            # exactamente 'numero' colores
            # ====================================================
            aviso_mostrado = {"valor": False}
            def callback(model, where):
                # MIPSOL se ejecuta cuando Gurobi encuentra
                # una nueva solucion factible.
                if where == GRB.Callback.MIPSOL:
                    # Obtener los valores de las variables y[c]
                    valores_y = model.cbGetSolution([y[c] for c in colores])
                    # Contar cuántos colores utiliza esta solucion
                    colores_usados = sum(1 for valor in valores_y if valor > 0.5)
                    # Si hemos llegado al número que buscamos
                    if (colores_usados == numero and not aviso_mostrado["valor"]):                       
                        print(f"Encontrada una coloracion con "f"{numero} colores usando GUROBI")
                        aviso_mostrado["valor"] = True
            # ====================================================
            # Resolver
            # ====================================================
            modelo.optimize(callback)
            # ====================================================
            # Recuperar la mejor solucion encontrada
            # ====================================================
            if modelo.SolCount == 0:
                return None, None
            coloracion = [-1] * n
            for v in vertices:
                for c in colores:
                    if x[v, c].X > 0.5:
                        coloracion[v] = c
                        break
            numero_colores = len(set(coloracion))
            print("Mejor coloracion encontrada:",numero_colores,"colores usando GUROBI")
            return coloracion, numero_colores
