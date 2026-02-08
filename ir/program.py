# ir/program.py

from ir.method import MethodIR


class ProgramIR:
    """
    Container for multiple methods.
    """
    def __init__(
        self,
        methods=None,
        fields=None,
        support_classes=None,
        method_class_map=None,
        lint_warnings=None,
        resources=None,
        resource_ids=None,
        resource_colors=None,
        resource_color_ids=None,
        resource_dimens=None,
        resource_dimen_ids=None,
        resource_styles=None,
        resource_style_ids=None,
    ):
        self.methods = methods or []
        self.fields = fields or []
        self.support_classes = support_classes or []
        self.method_class_map = method_class_map or {}
        self.lint_warnings = lint_warnings or []
        self.resources = resources or {}
        self.resource_ids = resource_ids or {}
        self.resource_colors = resource_colors or {}
        self.resource_color_ids = resource_color_ids or {}
        self.resource_dimens = resource_dimens or {}
        self.resource_dimen_ids = resource_dimen_ids or {}
        self.resource_styles = resource_styles or {}
        self.resource_style_ids = resource_style_ids or {}

    def add_method(self, method: MethodIR):
        self.methods.append(method)

    def add_field(self, field):
        self.fields.append(field)

    def add_support_class(self, class_desc: str, target_method: str, target_desc: str | None = None):
        if target_desc is None:
            self.support_classes.append((class_desc, target_method))
        else:
            self.support_classes.append((class_desc, target_method, target_desc))

    def add_resource_string(self, name: str, value: str):
        self.resources[name] = value

    def add_resource_id(self, name: str, value: int):
        self.resource_ids[name] = value

    def add_resource_color(self, name: str, value: str):
        self.resource_colors[name] = value

    def add_resource_color_id(self, name: str, value: int):
        self.resource_color_ids[name] = value

    def add_resource_dimen(self, name: str, value: str):
        self.resource_dimens[name] = value

    def add_resource_dimen_id(self, name: str, value: int):
        self.resource_dimen_ids[name] = value

    def add_resource_style(self, name: str, items: dict):
        self.resource_styles[name] = items

    def add_resource_style_id(self, name: str, value: int):
        self.resource_style_ids[name] = value
