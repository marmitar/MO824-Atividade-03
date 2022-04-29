from __future__ import annotations
from dataclasses import dataclass
from math import ceil, sqrt
import os.path

import gurobipy as gp


MAX_MINS = 30
DEBUG = False

env = gp.Env(empty=True)
env.setParam(gp.GRB.Param.OutputFlag, DEBUG)
env.setParam(gp.GRB.Param.LazyConstraints, True)
env.setParam(gp.GRB.Param.TimeLimit, MAX_MINS * 60)
env.start()


class Model(gp.Model):
    def __init__(self, *, name: str) -> None:
        super().__init__(name, env)
        self.params.OutputFlag = DEBUG
        self.params.LazyConstraints = True
        self.params.TimeLimit = MAX_MINS * 60


DEFAULT_FILE = os.path.join(os.path.dirname(__file__), 'coords.txt')

@dataclass(frozen=True)
class Point:
    x: int
    y: int

    @staticmethod
    def distance(u: Point, v: Point):
        return ceil(sqrt((u.x - v.x)**2 + (u.y - v.y)**2))

    @staticmethod
    def read(filename: str = DEFAULT_FILE):
        with open(filename, 'r') as file:
            for line in file:
                x1, y1, x2, y2 = map(int, line.strip().split())
                yield Point(x1, y1), Point(x2, y2)
