# ir/stmt.py

class Return:
    def __init__(self, value=None):
        self.value = value
        self.kind = "return"

    def defines(self):
        return None

    def uses(self):
        if self.value is None:
            return []
        return [self.value]

    def __repr__(self):
        return f"Return({self.value})"


class Throw:
    def __init__(self, value):
        self.value = value
        self.kind = "throw"

    def defines(self):
        return None

    def uses(self):
        return [self.value]

    def __repr__(self):
        return f"Throw({self.value})"


class TryCatch:
    def __init__(self, try_body, except_body, exception_type=None, handlers=None):
        self.try_body = try_body
        self.except_body = except_body
        self.exception_type = exception_type
        self.handlers = handlers

    def defines(self):
        return None

    def uses(self):
        return []

    def __repr__(self):
        return "TryCatch(...)"


class CallStmt:
    def __init__(self, expr):
        self.expr = expr

    def defines(self):
        return None

    def uses(self):
        return []

    def __repr__(self):
        return f"CallStmt({self.expr})"


class StaticFieldSet:
    def __init__(self, owner: str, name: str, desc: str, value):
        self.owner = owner
        self.name = name
        self.desc = desc
        self.value = value

    def defines(self):
        return None

    def uses(self):
        return [self.value]

    def __repr__(self):
        return f"sput {self.owner}->{self.name}:{self.desc} {self.value}"


class FieldSet:
    def __init__(self, obj, name: str, desc: str, owner: str, value):
        self.obj = obj
        self.name = name
        self.desc = desc
        self.owner = owner
        self.value = value

    def defines(self):
        return None

    def uses(self):
        return [self.obj, self.value]

    def __repr__(self):
        return f"iput {self.owner}->{self.name}:{self.desc} {self.value}"


class ArraySet:
    def __init__(self, array, index, elem_desc: str, value):
        self.array = array
        self.index = index
        self.elem_desc = elem_desc
        self.value = value

    def defines(self):
        return None

    def uses(self):
        return [self.array, self.index, self.value]

    def __repr__(self):
        return f"aput {self.elem_desc} {self.value}"
