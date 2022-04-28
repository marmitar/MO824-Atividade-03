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
