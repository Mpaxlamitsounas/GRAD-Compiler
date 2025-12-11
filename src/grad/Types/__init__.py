from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class OperandType(Enum):
    Register = auto()
    Constant = auto()


@dataclass(frozen=True)
class Operand:
    type: OperandType
    value: str = ""
    pointer: Optional["Operand"] = None

    def __str__(self):
        return f"M[{self.pointer}]" if self.pointer is not None else self.value

    def __repr__(self):
        return self.__str__()


class Condition(Enum):
    GE = ">="
    TRUE = ""


@dataclass
class JumpType:
    condition: Condition
    compared: Operand | None
    destination: str | None

    def copy(self):
        return JumpType(self.condition, self.compared, self.destination)
