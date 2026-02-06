# ir/program.py

from ir.method import MethodIR


class ProgramIR:
    """
    Container for multiple methods.
    """
    def __init__(self, methods=None, fields=None):
        self.methods = methods or []
        self.fields = fields or []

    def add_method(self, method: MethodIR):
        self.methods.append(method)

    def add_field(self, field):
        self.fields.append(field)
