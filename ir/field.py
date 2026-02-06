# ir/field.py


class StaticField:
    def __init__(self, name: str, desc: str, access: str = "private static"):
        self.name = name
        self.desc = desc
        self.access = access

    def __repr__(self):
        return f".field {self.access} {self.name}:{self.desc}"
