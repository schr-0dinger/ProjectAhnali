# ir/program.py

from ir.method import MethodIR


class ProgramIR:
    """
    Container for multiple methods.
    """
    def __init__(self, methods=None):
        self.methods = methods or []

    def add_method(self, method: MethodIR):
        self.methods.append(method)
