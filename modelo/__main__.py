from argparse import ArgumentParser
from time import time
from typing import Iterable, TypeVar

import gurobipy as gp
from .model import Point
from .tsp import EdgeDict
from .kstsp import ksTSP


Item = TypeVar('Item')

def take(it: Iterable[Item], n: int):
    for i, value in enumerate(it):
        if i < n:
            yield value
        else:
            return


def two_tsp(vertices: Iterable[tuple[Point, Point]], k: int):
    problem = ksTSP.dual_model(vertices, k)
    problem.add_shared_edge_constraint()
    problem.solution()
    return problem


def zero(first: Iterable[EdgeDict[float]], second: Iterable[EdgeDict[float]], tol: float):
    for df, ds in zip(first, second):
        for xf, xs in zip(df.values(), ds.values()):
            if abs(xf - xs) > tol:
                return False
    return True


def iter_grad(problem: ksTSP, pi: float, l0: float, tol: float=1e-8):
    Zub = problem.upper_bound()
    print('Upper bound:', Zub)

    alpha = 0.0
    lm = problem.initial_multipliers(l0)
    while True:
        Zlb = problem.solution(lm)
        yield Zlb

        g = problem.subgradient()
        alpha = pi * (Zub - Zlb) / sum(value**2 for gi in g for value in gi.values())
        pi = 0.99 * pi

        next_lm = tuple(
            gp.tupledict({
                uv: max(0, lme + alpha * g[i][uv])
                for uv, lme in lmi.items()
            })
            for i, lmi in enumerate(lm)
        )
        if zero(lm, next_lm, tol):
            return
        else:
            lm = next_lm


def subgradient(vertices: Iterable[tuple[Point, Point]], k: int, pi: float, max_iter: int, l0: float):
    problem = ksTSP.dual_model(vertices, k)

    for i, Zlb in enumerate(iter_grad(problem, pi, l0)):
        print(f'Lower bound (it {i}):', Zlb)

        if i > max_iter:
            raise ValueError('max iteration reached', i)
    return problem


parser = ArgumentParser('modelo')
parser.add_argument('-2', '--2TSP', action='store_true', dest='twotsp',
    help='use the model without the lagrangean relaxation')
parser.add_argument('-k', type=int, default=0,
    help='similarity (default: 0)')
parser.add_argument('-v', '--vertices', type=int, default=100,
    help='graph order (default: 100)')
parser.add_argument('-pi', type=float, default=1.0,
    help='initial step size multiplier (default: 1.0)')
parser.add_argument('-m', '--max-iter', type=int, default=100,
    help='max number of iterations on subgradient method (default: 100)')
parser.add_argument('-l0', type=float, default=0.0,
    help='initial lambda value (default: 0.0)')
args = parser.parse_intermixed_args()


vertices = take(Point.read(), args.vertices)
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
