from dataclasses import dataclass
from typing import Iterable, Literal

import gurobipy as gp
from .model import Model, Point
from .tsp import EdgeDict, TSP


@dataclass(frozen=True)
class ksTSP:
    vertices: tuple[tuple[Point, Point], ...]
    k: int
    cycle1: TSP
    cycle2: TSP
    ze: EdgeDict[gp.Var]

    @property
    def size(self):
        return self.cycle1.size

    @property
    def model(self):
        return self.cycle1.model

    def pairs(self):
        return self.cycle1.pairs()

    @staticmethod
    def dual_model(vertices: Iterable[tuple[Point, Point]], k: int):
        vertices = tuple(vertices)

        model = Model(name='ksTSP')
        cycle1 = TSP.from_model(len(vertices), model, varname='e1')
        cycle2 = TSP.from_model(len(vertices), model, varname='e2')

        ze = model.addVars(cycle1.pairs(), vtype=gp.GRB.BINARY, name='z')
        model.addConstr(ze.sum() >= k)

        return ksTSP(vertices, k, cycle1, cycle2, ze)

    def add_shared_edge_constraint(self):
        self.model.addConstrs(self.cycle1.edges[uv] >= self.ze[uv] for uv in self.pairs())
        self.model.addConstrs(self.cycle2.edges[uv] >= self.ze[uv] for uv in self.pairs())

    def subtour_elim(self, where: int):
        self.cycle1.subtour_elim(where)
        self.cycle2.subtour_elim(where)

    def distance(self, cycle: Literal[1, 2], u: int, v: int):
        return Point.distance(self.vertices[u][cycle-1], self.vertices[v][cycle-1])

    def initial_multipliers(self, value: float = 1.0):
        lm = gp.tupledict({uv: value for uv in self.pairs()})
        return lm, lm

    def subgradient(self):
        x1, x2 = self.cycle1.edges, self.cycle2.edges
        g1 = gp.tupledict({uv: self.ze[uv].X - x1[uv].X for uv in self.pairs()})
        g2 = gp.tupledict({uv: self.ze[uv].X - x2[uv].X for uv in self.pairs()})

        return g1, g2

    def objective_2tsp(self):
        return (
            self.cycle1.objective(lambda u, v: self.distance(1, u, v))
            + self.cycle2.objective(lambda u, v: self.distance(2, u, v))
        )

    def objective_lagrange(self, multipliers: tuple[EdgeDict[float], EdgeDict[float]]):
        (lm1, lm2), x1, x2 = multipliers, self.cycle1.edges, self.cycle2.edges
        return (
            self.objective_2tsp()
            + gp.quicksum(lm1[uv] * (self.ze[uv] - x1[uv]) for uv in self.pairs())
            + gp.quicksum(lm2[uv] * (self.ze[uv] - x2[uv]) for uv in self.pairs())
        )

    def upper_bound(self):
        def distsum(u: int, v: int):
            return self.distance(1, u, v) + self.distance(2, u, v)
        return TSP.solution(self.size, distsum).minimum_cost

    def solution(self, multipliers: tuple[EdgeDict[float], EdgeDict[float]] | None = None):
        if multipliers is None:
            self.model.setObjective(self.objective_2tsp(), gp.GRB.MINIMIZE)
        else:
            self.model.setObjective(self.objective_lagrange(multipliers), gp.GRB.MINIMIZE)

        self.model.optimize(lambda _, where: self.subtour_elim(where))
        if self.model.SolCount < 1:
            raise ValueError('could not find a solution', self)

        return self.model.ObjVal
