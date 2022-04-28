from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from math import ceil, sqrt
from typing import cast, Sequence, TypeVar

import gurobipy as gp
from .model import Model


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def dist(self, other: Point):
        return ceil(sqrt((self.x - other.x)**2 + (self.y - other.y)**2))


T = TypeVar('T')
EdgeDict = gp.tupledict[tuple[int, int], T]


def build_tsp(coords: Sequence[Point], varname: str = 'e', model: Model | None = None):
    if model is None:
        model = Model(name='TSP')

    dist = {
        (u, v): pu.dist(pv)
        for (u, pu), (v, pv) in combinations(enumerate(coords), 2)
    }

    edges = model.addVars(dist.keys(), name=varname, vtype=gp.GRB.BINARY)
    for (u, v), var in edges.items():
        edges[v, u] = var

    model.addConstrs(edges.sum(u, '*') for u in range(len(coords)))

    return model, cast(EdgeDict[gp.Var], edges)


def subtour(solution: EdgeDict[float], size: int):
    edges = gp.tuplelist(uv for uv, link in solution.items() if link > 0.5)

    unvisited = set(range(size))
    min_cycle = tuple(range(size + 1))

    while unvisited:
        cycle: list[int] = []
        neighbors = unvisited
        while neighbors:
            u = neighbors.pop()
            cycle.append(u)
            neighbors = {v for _, v in edges.select(u, '*') if v in unvisited}

        if len(cycle) < len(min_cycle):
            min_cycle = tuple(cycle)
    return min_cycle


def subtour_elim(edges: EdgeDict[gp.Var], size: int):
    def callback(model: Model, where: int):
        if where == gp.GRB.Callback.MIPSOL:
            solution = model.cbGetSolution(edges)
            tour = subtour(solution, size)

            if len(tour) < size:
                model.cbLazy(
                    gp.quicksum(edges[u, v] for u, v in combinations(tour, 2)),
                    gp.GRB.LESS_EQUAL,
                    len(tour) - 1
                )

    return callback


# def solve_tsp(coords: Sequence[Point], )
