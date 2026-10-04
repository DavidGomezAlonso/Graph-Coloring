from src.leer_grafo import leer_grafo
from src.dsatur import dsatur_greedy
from src.colorear_grafo_gurobi import colorear_grafo_gurobi
from src.tabuCol import optimo_tabu_col
import time
from src.guardar_coloracion import guardar_mejor_coloracion
nodos,aristas,vecinos=leer_grafo("data/gc_100_1")
print("Hay",nodos,"nodos y",aristas,"aristas")
coloracion_inicial=dsatur_greedy(vecinos)
num_colors=max(coloracion_inicial)
print("Se ha encontrado una coloracion inicial con",num_colors,"usando algoritmo DSATUR greedy")
seed=12345
inicio=time.perf_counter()
coloracion1= optimo_tabu_col(vecinos,coloracion_inicial,1000,3,seed,False)
print("Se ha encontrado una coloracion con",max(coloracion1)+1,"colores usando TabuCol")
guardar_mejor_coloracion(coloracion1)
fin=time.perf_counter()
tiempoTabu=(fin-inicio)*1000
print("Tiempo de ejecucion TabuCol:",tiempoTabu,"ms\n")

inicio=time.perf_counter()
coloracion2,num_colors2=colorear_grafo_gurobi(vecinos,max(coloracion1)+1,coloracion_inicial,300)
fin=time.perf_counter()
tiempo=(fin-inicio)*1000
print("Tiempo de ejecucion GUROBI + Greedy:",tiempo,"ms\n")

print("\nColoracion TabuCol:\n",coloracion1)
