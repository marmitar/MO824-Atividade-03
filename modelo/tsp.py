from dataclasses import dataclass
from itertools import combinations
from typing import Callable, TypeVar

import gurobipy as gp
from .model import Model


Value = TypeVar('Value')
EdgeDict = gp.tupledict[tuple[int, int], Value]


@dataclass(frozen=True)
class TSP:
    size: int
    model: Model
    edges: EdgeDict[gp.Var]

    @property
    def vertices(self):
        return range(self.size)

    def pairs(self):
        return combinations(self.vertices, 2)

    @staticmethod
    def from_model(size: int, model: Model, *, varname: str = 'e'):
        pairs = combinations(range(size), 2)
        edges = model.addVars(pairs, name=varname, vtype=gp.GRB.BINARY)
        for (u, v), var in edges.items():
            edges[v, u] = var

        model.addConstrs(edges.sum(u, '*') == 2 for u in range(size))
        return TSP(size, model, edges)

    def full_cycle(self):
        return tuple(self.vertices) + (0,)

    def subtour(self, solution: EdgeDict[float]):
        edges = gp.tuplelist(uv for uv, link in solution.items() if link > 0.5)
        unvisited = set(self.vertices)
        min_cycle = self.full_cycle()

        while unvisited:
            cycle: list[int] = []
            neighbors = set(unvisited)
            while neighbors:
                u = neighbors.pop()
                cycle.append(u)
                unvisited.remove(u)
                neighbors = {v for _, v in edges.select(u, '*') if v in unvisited}

            if len(cycle) < len(min_cycle):
                min_cycle = tuple(cycle)
        return min_cycle

    def subtour_elim(self, where: int):
        if where == gp.GRB.Callback.MIPSOL:
            solution = self.model.cbGetSolution(self.edges)
            tour = self.subtour(solution)

            if len(tour) < self.size:
                edge_count = gp.quicksum(self.edges[u, v] for u, v in combinations(tour, 2))
                self.model.cbLazy(edge_count <= len(tour) - 1)

    def objective(self, weight: Callable[[int, int], float]):
        return gp.quicksum(weight(u, v) * self.edges[u, v] for u, v in self.pairs())

    @property
    def minimum_cost(self):
        return self.model.ObjVal

    @staticmethod
    def solution(size: int, weight: Callable[[int, int], float]):
        problem = TSP.from_model(size, Model(name='TSP'))
        problem.model.update()
        problem.model.setObjective(problem.objective(weight), gp.GRB.MINIMIZE)
        problem.model.optimize(lambda _, where: problem.subtour_elim(where))

        if problem.model.SolCount < 1:
            raise ValueError('could not find a solution', problem)
        return problem
