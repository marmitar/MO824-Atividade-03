from argparse import ArgumentParser
from time import time
from typing import Iterable, TypeVar

import gurobipy as gp
from .model import Point
from .kstsp import ksTSP


T = TypeVar('T')

def take(it: Iterable[T], n: int):
    for i, value in enumerate(it):
        if i < n:
            yield value


def two_tsp(vertices: Iterable[tuple[Point, Point]], k: int):
    problem = ksTSP.dual_model(vertices, k)
    problem.add_shared_edge_constraint()
    problem.solution()
    return problem


def iter_grad(problem: ksTSP, pi: float, l0: float, tol=1e-5):
    Zub = problem.upper_bound()

    lm = problem.initial_multipliers(l0)
    Zlb_prev = Zub
    Zlb = problem.solution(lm)
    yield Zlb

    while abs(Zlb - Zlb_prev) > tol:
        g = problem.subgradient()
        alpha = pi * (Zub - Zlb) / sum(value * value for gi in g for value in gi.values())
        for i, lmi in enumerate(lm):
            lmie = gp.tupledict({lme + alpha * g[i][uv]  for uv, lme in lmi.items()})
            lm[i] = max(0, lmie)

        Zlb_prev, Zlb = Zlb, problem.solution(lm)
        yield Zlb


def subgradient(vertices: Iterable[tuple[Point, Point]], k: int, pi: float, max_iter: int, l0: float):
    problem = ksTSP.dual_model(vertices, k)

    for i, _ in enumerate(iter_grad(problem, pi, l0)):
        if i > max_iter:
            raise ValueError('max iteration reached', i)
    return problem


parser = ArgumentParser('modelo')
parser.add_argument('filename')
parser.add_argument('-2', '--2TSP', action='store_true', dest='twotsp')
parser.add_argument('-k', type=int, default=0)
parser.add_argument('-v', '--vertices', type=int, default=250)
parser.add_argument('-pi', type=float, default=1.0)
parser.add_argument('-m', '--max-iter', type=int, default=1_000)
parser.add_argument('-l0', type=float, default=1.0)
args = parser.parse_intermixed_args()


vertices = take(Point.read(args.filename), args.vertices)
start = time()
if args.twotsp:
    problem = two_tsp(vertices, args.k)
else:
    problem = subgradient(vertices, args.k, args.pi, args.max_iter, args.l0)
elapsed = time() - start

print(f'Minimum Cost: {problem.min_cost}')
print(f'Num Vars: {problem.num_vars}')
print(f'Num Consts: {problem.num_constrs}')
print(f'Execution time: {elapsed} s')
