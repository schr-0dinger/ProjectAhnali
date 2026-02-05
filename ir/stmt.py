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


class TryCatch:
    def __init__(self, try_body, except_body, exception_type=None):
        self.try_body = try_body
        self.except_body = except_body
        self.exception_type = exception_type

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
