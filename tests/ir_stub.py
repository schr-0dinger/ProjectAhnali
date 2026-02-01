# tests/ir_stub.py

class Assign:
    def __init__(self, name, expr=None):
        self.name = name
        self.expr = expr

    def uses(self):
        if isinstance(self.expr, str):
            return [Var(self.expr)]
        return []

    def defines(self):
        return Var(self.name)

    def replace_def(self, ssa_value):
        self.defines = lambda: ssa_value

    def __repr__(self):
        return f"{self.name} = {self.expr}"


class Var:
    def __init__(self, name):
        self.name = name

    def replace_with(self, ssa_value):
        self.name = ssa_value

    def __repr__(self):
        return f"{self.name}"


class If:
    def __init__(self, cond, then, else_):
        self.cond = cond
        self.then = then
        self.else_ = else_


class While:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
