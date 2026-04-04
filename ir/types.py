# ir/types.py
from enum import Enum, auto

class AhnaliType(Enum):
    INT = auto()
    LONG = auto()
    FLOAT = auto()
    DOUBLE = auto()
    BOOL = auto()
    STRING = auto()
    OBJECT = auto()
    UNKNOWN = auto()

    def __repr__(self):
        return self.name
