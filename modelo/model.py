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
env.start()


class Model(gp.Model):
    def __init__(self, *, name: str) -> None:
        super().__init__(name, env)
        self.params.OutputFlag = DEBUG
        self.params.LazyConstraints = True


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


def register_alarm(after_secs: float | int):
    from signal import alarm, signal, SIGALRM
    from time import time
    from types import FrameType
    import sys

    start = time()

    def handler(signum: int, frame: FrameType | None = None):
        if signum == SIGALRM:
            end = time()
            print(f'Execution timeout after {end - start} s')
            if frame:
                print('Current frame:', frame)

            sys.exit(1)


    signal(SIGALRM, handler)
    alarm(ceil(after_secs))


register_alarm(MAX_MINS * 60)
