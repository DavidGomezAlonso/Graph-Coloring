# Graph Coloring: DSATUR, TabuCol and Gurobi
 
This repository compares heuristic and exact methods for the **graph coloring problem** (assign a color to every vertex so that no two adjacent vertices share one, using as few colors as possible) by chaining three approaches:
 
1. **DSATUR**: a fast greedy heuristic that produces an initial valid coloring.
2. **TabuCol**: a tabu search metaheuristic, compiled with Numba, that repeatedly tries to remove one color from the best coloring found so far.
3. **Gurobi**: an exact integer programming model, warm-started with the greedy coloring, used to improve on or certify the heuristic result.
> Identifiers and console messages in the code are in Spanish (`vecinos` = neighbors, `coloracion` = coloring, `aristas` = edges, `nodos` = vertices).
 
## Project structure
 
```
.
├── main.py                        # Runs the full pipeline on one instance
├── data/
│   └── gc_100_1                   # Graph instance
└── src/
    ├── leer_grafo.py              # Instance reader
    ├── dsatur.py                  # DSATUR greedy heuristic
    ├── tabuCol.py                 # TabuCol local search (Numba)
    ├── colorear_grafo_gurobi.py   # Integer programming model (Gurobi)
    └── guardar_coloracion.py      # Stores the best coloring found
```
 
## Requirements
 
- Python 3
- [NumPy](https://numpy.org/)
- [Numba](https://numba.pydata.org/)
- [gurobipy](https://pypi.org/project/gurobipy/) and a Gurobi license
```bash
pip install numpy numba gurobipy
```
 
The license bundled with the `gurobipy` pip package is size-limited (2,000 variables and 2,000 constraints). The model has one constraint per edge and color, so all but the smallest instances need a full license. Academic licenses are free.
 
## Usage
 
Run from the repository root, since the instance path and the `src` imports are relative to it:
 
```bash
python main.py
```
 
The script prints the size of the graph, the number of colors found by each method and the running time of each stage:
 
```
Hay <n> nodos y <m> aristas
Se ha encontrado una coloracion inicial con <k0> usando algoritmo DSATUR greedy
Se ha encontrado una coloracion con <k1> colores usando TabuCol
Nueva mejor coloracion guardada: <k1> colores
Tiempo de ejecucion TabuCol: <t> ms
 
Encontrada una coloracion con <k1> colores usando GUROBI
Mejor coloracion encontrada: <k2> colores usando GUROBI
Tiempo de ejecucion GUROBI + Greedy: <t> ms
 
Coloracion TabuCol:
 [...]
```
 
### Configuration
 
Everything is set directly in `main.py`:
 
| Setting | Value in `main.py` | Meaning |
| --- | --- | --- |
| Instance | `"data/gc_100_1"` | Path of the graph to color |
| `seed` | `12345` | Seed for TabuCol, which makes runs reproducible |
| Iterations per attempt | `1000` | TabuCol iteration limit for each attempt |
| Attempts | `3` | Restarts allowed for each target number of colors |
| Verbose | `False` | Set to `True` to print the progress of every attempt |
| Gurobi time limit | `300` | Seconds before Gurobi returns its best solution |
 
## Input format
 
Plain text. The first line holds the number of vertices and the number of edges; each following line is one edge given by its two endpoints. Vertices are numbered from `0`.
 
```
4 3
0 1
1 2
1 3
```
 
## Output file
 
The TabuCol coloring is written to `coloracion.txt`, but only if it uses fewer colors than the coloring already stored there:
 
```
<number of colors>
<color of vertex 0> <color of vertex 1> ... <color of vertex n-1>
```
 
The file is not tied to a particular instance, so delete it before switching to a different graph.
 
## Algorithms
 
### DSATUR (`src/dsatur.py`)
 
The vertex of highest degree is colored first. After that, the next vertex is always the uncolored one with the highest *saturation* (number of distinct colors among its neighbors), with ties broken by degree. Each vertex receives the smallest color not used by its neighbors. Colors are numbered from `1`.
 
### TabuCol (`src/tabuCol.py`)
 
For a fixed number of colors `k`, TabuCol searches the space of (possibly invalid) `k`-colorings and minimizes the number of conflicting edges.
 
- **Moves.** Change the color of one vertex that is currently in conflict. Every iteration applies the best non-tabu move, with ties broken uniformly at random.
- **Incremental evaluation.** A matrix `gamma[v][c]` stores how many neighbors of `v` have color `c`, so the effect of a move is `gamma[v][new] - gamma[v][old]` and only the neighbors of the moved vertex need updating.
- **Tabu list.** After moving `v` away from color `c`, returning `v` to `c` is forbidden for `3 * nc // 5 + r` iterations, where `nc` is the number of conflicting vertices and `r` is a random integer in `[0, 9]`.
- **Aspiration.** A tabu move is still allowed if it leads to fewer conflicts than the best solution seen so far.
- **Performance.** The search loop is compiled with `@njit(cache=True)` and the graph is stored in CSR form (`offsets` and `adyacentes` arrays).
The driver `optimo_tabu_col` starts from the DSATUR coloring with `k` colors and targets `k - 1`: vertices whose color is no longer available are recolored at random and TabuCol runs for up to `reintentos` attempts. If a valid coloring is found, the target drops again; the procedure stops at the first number of colors for which every attempt fails.
 
### Integer programming model (`src/colorear_grafo_gurobi.py`)
 
With `x[v,c] = 1` if vertex `v` takes color `c` and `y[c] = 1` if color `c` is used:
 
```math
\begin{aligned}
\min \quad & \sum_{c} y_c \\
\text{s.t.} \quad & \sum_{c} x_{vc} = 1 && \forall v \in V \\
& x_{uc} + x_{vc} \le 1 && \forall (u,v) \in E,\ \forall c \\
& x_{vc} \le y_c && \forall v \in V,\ \forall c \\
& x_{vc},\ y_c \in \{0,1\}
\end{aligned}
```
 
The number of colors available to the model is the number used by the initial coloring, which is a valid upper bound. Three sets of symmetry-breaking conditions reduce the search space:
 
- vertex `0` takes color `0`;
- vertex `v` never takes a color greater than `v`;
- colors are used in order: `y[c] >= y[c+1]`.
The initial coloring is relabeled by order of first appearance, which satisfies these conditions, and passed to Gurobi as a MIP start. A callback prints a message the first time Gurobi finds a solution with exactly `numero` colors; `main.py` uses this to report when Gurobi matches the TabuCol result.
 
## API
 
| Function | Returns | Description |
| --- | --- | --- |
| `leer_grafo(ruta)` | `(nodos, aristas, vecinos)` | Reads an instance; `vecinos` is the adjacency list |
| `dsatur_greedy(vecinos)` | `list[int]` | Valid coloring with colors starting at `1` |
| `optimo_tabu_col(vecinos, colores, max_iter_intento=100000, reintentos=3, seed=12345, narra=False)` | sequence of `int` | Best valid coloring found, with colors `0..k-1` |
| `colorear_grafo_gurobi(vecinos, numero, coloracion_inicial=[], tiempo_max=None)` | `(coloracion, numero_colores)` | Best coloring found by Gurobi, or `(None, None)` if there is none |
| `guardar_mejor_coloracion(solucion, archivo="coloracion.txt")` | `bool` | Saves the coloring if it improves the stored one |
 
Example:
 
```python
from src.leer_grafo import leer_grafo
from src.dsatur import dsatur_greedy
from src.tabuCol import optimo_tabu_col
 
nodos, aristas, vecinos = leer_grafo("data/gc_100_1")
inicial = dsatur_greedy(vecinos)
coloracion = optimo_tabu_col(vecinos, inicial, max_iter_intento=100000, reintentos=3, seed=12345, narra=True)
print(max(coloracion) + 1, "colors")
```
 
## Notes
 
- The first run includes Numba's compilation time in the TabuCol timing. Later runs reuse the cached compilation.
- `optimo_tabu_col` renumbers the list it receives in place, so the colors of the initial coloring start at `0` after the call.
- TabuCol is a heuristic: the number of colors it returns is an upper bound on the chromatic number. Gurobi proves optimality only if it finishes before the time limit.
## References
 
- D. Brélaz, "New methods to color the vertices of a graph", *Communications of the ACM*, 22(4), 1979.
- A. Hertz and D. de Werra, "Using tabu search techniques for graph coloring", *Computing*, 39, 1987.
