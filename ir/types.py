# ir/types.py
from enum import Enum, auto

class AnaliType(Enum):
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STRING = auto()
    OBJECT = auto()
    UNKNOWN = auto()

    def __repr__(self):
        return self.name
