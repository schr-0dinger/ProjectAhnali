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
