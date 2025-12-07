from dataclasses import dataclass
from enum import Enum, auto


class Condition(Enum):
    GE = ">="
    TRUE = ""


class OperandType(Enum):
    Register = auto()
    Constant = auto()


@dataclass(frozen=True)
class Operand:
    type: OperandType
    name: str = ""
    value: str = ""

    def __str__(self):
        if self.name == "M":
            return f"M[{self.value}]"

        elif self.type == OperandType.Register:
            return self.name

        else:
            return self.value

    def __repr__(self):
        return self.__str__()


@dataclass
class JumpType:
    condition: Condition
    compared: Operand | None
    destination: str
