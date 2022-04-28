from collections import namedtuple
from datetime import datetime
from itertools import combinations
from math import ceil, sqrt
import gurobipy as gp
import networkx as nx
from gurobipy import *

Coord = namedtuple(
    'Coord',

    'x1 '
    'y1 '
    'x2 '
    'y2 '
)


def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        valsTsp1 = model.cbGetSolution(model._varTsp1)
        valsTsp2 = model.cbGetSolution(model._varTsp2)

        tour = subtour(valsTsp1)
        if len(tour) < n:
            model.cbLazy(gp.quicksum(model._varTsp1[i, j] for i, j in combinations(tour, 2)) <= len(tour) - 1)

        tour = subtour(valsTsp2)
        if len(tour) < n:
            model.cbLazy(gp.quicksum(model._varTsp2[i, j] for i, j in combinations(tour, 2)) <= len(tour) - 1)


def subtour(vals):
    edges = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)
    unvisited = list(range(n))
    cycle = range(n + 1)
    while unvisited:
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle


def draw_graph(tsp1, tsp2, original_edges):
    usedEdgesTsp1 = [(i, j) for i, j in tsp1.keys() if tsp1[i, j] > 0.5]
    usedEdgesTsp2 = [(i, j) for i, j in tsp2.keys() if tsp2[i, j] > 0.5]

    edges = []
    for i, j in original_edges:
        edges.append((i, j))
        edges.append((j, i))

    G = nx.DiGraph()

    for i, j in edges:
        G.add_edge(i, j)
        G.add_edge(j, i)
        
    purple_edges = [edge for edge in G.edges() if edge in usedEdgesTsp2 and edge in usedEdgesTsp1]

    print('Common edges = {}'.format(len(purple_edges)))


def read_coordinates():
    coordinates = []

    with open('coords') as f:
        lines = f.readlines()

        for line in lines:
            x1, y1, x2, y2 = [int(i) for i in line.split(" ")]
            coordinates.append(Coord(x1, y1, x2, y2))

    return coordinates


def run_model(coords, k):
    n = len(coords)

    dist1 = {
        (i, j): ceil(sqrt((coords[i].x1 - coords[j].x1) ** 2 + (coords[i].y1 - coords[j].y1) ** 2))
        for i in range(n)
        for j in range(i)
    }

    dist2 = {
        (i, j): ceil(sqrt((coords[i].x2 - coords[j].x2) ** 2 + (coords[i].y2 - coords[j].y2) ** 2))
        for i in range(n)
        for j in range(i)
    }

    m = gp.Model()

    # Create variables
    varTsp1 = m.addVars(dist1.keys(), obj=dist1, vtype=GRB.BINARY, name='e1')
    varTsp2 = m.addVars(dist2.keys(), obj=dist2, vtype=GRB.BINARY, name='e2')
    varIsInBothTsp = m.addVars(dist2.keys(), vtype=GRB.BINARY, name="z")

    for i, j in varTsp1.keys():
        varTsp1[j, i] = varTsp1[i, j]
        varTsp2[j, i] = varTsp2[i, j]

    m.addConstrs(varTsp1.sum(i, '*') == 2 for i in range(n))
    m.addConstrs(varTsp2.sum(i, '*') == 2 for i in range(n))

    m.addConstr(sum(varIsInBothTsp[i, j] for i, j in dist2.keys()) >= k)

    for i, j in dist2.keys():
        m.addConstr(varIsInBothTsp[i, j] <= varTsp1[i, j])
        m.addConstr(varIsInBothTsp[i, j] <= varTsp2[i, j])
        m.addConstr(varIsInBothTsp[i, j] >= (varTsp2[i, j] + varTsp1[i, j] - 1))

    m._varTsp1 = varTsp1
    m._varTsp2 = varTsp2
    m.Params.LazyConstraints = 1

    m.setParam('TimeLimit', 60*30)

    m.ModelSense = GRB.MINIMIZE

    start = datetime.now()
    m.optimize(subtourelim)
    totalTime = datetime.now() - start
    print("Total time in seconds: ", totalTime.total_seconds())

    if m.SolCount > 0:
        print_solution(m, varTsp1, varTsp2, dist1.keys())

    return m


def print_solution(m, var_tsp_1, var_tsp_2, edges):
    m.Params.SolutionNumber = 0

    valsTsp1 = m.getAttr('X', var_tsp_1)
    valsTsp2 = m.getAttr('X', var_tsp_2)

    tour1 = subtour(valsTsp1)
    tour2 = subtour(valsTsp2)

    draw_graph(valsTsp1, valsTsp2, edges)

    assert len(tour1) == n
    assert len(tour2) == n

    print('Optimal tour 1: %s' % str(tour1))
    print('Optimal tour 2: %s' % str(tour2))
    print('Optimal cost: %g' % m.ObjVal)


if __name__ == "__main__":
    N = [100, 150, 200, 250]
    coords = read_coordinates()

    for n in N:
        for k in [0, n / 2, n]:
            file = open('results/N{}K{}'.format(n, k), 'w')
            sys.stdout = file
            newCords = coords[0:n]

            model = run_model(newCords, k)

            print("|V| = {} ".format(n))
            print("k = {} ".format(k))
            print("Optimal cost = {} ".format(model.ObjVal))
            print("Solutions count = {} ".format(model.SolCount))


