from ir.expr import BinaryOp, Var as IRVar

class Ref:
    """Helper to allow in-place modification of object attributes"""
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

    @property
    def name(self):
        val = getattr(self.obj, self.attr)
        if isinstance(val, IRVar):
            return val.name
        return val

    def replace_with(self, new_val):
        setattr(self.obj, self.attr, new_val)

class Assign:
    def __init__(self, name, expr=None):
        self.name = name
        self.expr = expr

    def uses(self):
        if isinstance(self.expr, str):
            from tests.ir_stub import Var # Local Var stub
            return [Var(self.expr)]
            
        if isinstance(self.expr, BinaryOp):
            uses_list = []
            # Check left operand (Var or SSAValue)
            if hasattr(self.expr.left, "name"):
                uses_list.append(Ref(self.expr, 'left'))
            
            # Check right operand
            if hasattr(self.expr.right, "name"):
                uses_list.append(Ref(self.expr, 'right'))
                
            return uses_list

        return []

    def defines(self):
        # We return a Var stub that has .name
        return Var(self.name)

    def replace_def(self, ssa_value):
        # Allow checking .defines().name by returning a mock object that returns ssa_value
        # This is a bit hacky but consistent with original stub
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


class TryCatch:
    def __init__(self, try_body, except_body, exception_type=None):
        self.try_body = try_body
        self.except_body = except_body
        self.exception_type = exception_type
