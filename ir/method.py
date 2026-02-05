# ir/method.py

class MethodIR:
    def __init__(self, name, params=None, body=None, return_type=None, param_types=None):
        self.name = name
        self.params = params or []
        self.body = body or []
        self.return_type = return_type
        self.param_types = param_types or []
