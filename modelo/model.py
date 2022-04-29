from __future__ import annotations
from dataclasses import dataclass
from math import ceil, sqrt

import gurobipy as gp


MAX_MINS = 30

env = gp.Env(empty=True)
env.setParam(gp.GRB.Param.OutputFlag, 0)
env.setParam(gp.GRB.Param.LazyConstraints, 1)
env.setParam(gp.GRB.Param.TimeLimit, MAX_MINS * 60)
env.start()


class Model(gp.Model):
    def __init__(self, *, name: str) -> None:
        super().__init__(name, env)
        self.params.OutputFlag = 0
        self.params.LazyConstraints = 1
        self.params.TimeLimit = MAX_MINS * 60


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    @staticmethod
    def distance(u: Point, v: Point):
        return ceil(sqrt((u.x - v.x)**2 + (u.y - v.y)**2))

    @staticmethod
    def read(filename: str):
        with open(filename, 'r') as file:
            for line in file:
                x1, y1, x2, y2 = map(int, line.strip().split())
                yield Point(x1, y1), Point(x2, y2)
