# ir/program.py

from ir.method import MethodIR


class ProgramIR:
    """
    Container for multiple methods.
    """
    def __init__(self, methods=None, fields=None, support_classes=None, resources=None, resource_ids=None):
        self.methods = methods or []
        self.fields = fields or []
        self.support_classes = support_classes or []
        self.resources = resources or {}
        self.resource_ids = resource_ids or {}

    def add_method(self, method: MethodIR):
        self.methods.append(method)

    def add_field(self, field):
        self.fields.append(field)

    def add_support_class(self, class_desc: str, target_method: str):
        self.support_classes.append((class_desc, target_method))

    def add_resource_string(self, name: str, value: str):
        self.resources[name] = value

    def add_resource_id(self, name: str, value: int):
        self.resource_ids[name] = value
