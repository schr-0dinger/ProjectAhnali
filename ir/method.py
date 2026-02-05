# ir/method.py

class MethodIR:
    def __init__(self, name, params=None, body=None):
        self.name = name
        self.params = params or []
        self.body = body or []
