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


@dataclass(frozen=True)
class ConditionType:
    value: str
    bit_repr: int


@dataclass
class JumpType:
    condition: ConditionType
    compared: Operand | None
    destination: str | None

    def copy(self):
        return JumpType(self.condition, self.compared, self.destination)

    def __str__(self):
        # ConditionType("", 7) == Conditions.TRUE
        s = "IF " if self.condition != ConditionType("", 7) else ""
        s += self.condition.value
        s += f" {self.compared} " if self.condition != ConditionType("", 7) else ""
        s += "JMP"
        s += f" {self.destination}" if self.destination is not None else ""
        return s


class Multiplicity(Enum):
    UNARY = 1
    BINARY = 2


@dataclass
class OperationType:
    symbol: str
    multiplicity: Multiplicity
    bit_repr: int

    def __str__(self):
        if self.symbol == "_/":
            return self.symbol + "{}"
        elif self.multiplicity == Multiplicity.UNARY:
            return self.symbol + "{}" + self.symbol
        else:
            return "{} " + self.symbol + " {}"


class Operation:
    AND = OperationType("&", Multiplicity.BINARY, 0)
    OR = OperationType("|", Multiplicity.BINARY, 1)
    NOT = OperationType("~", Multiplicity.UNARY, 2)
    ADD = OperationType("+", Multiplicity.BINARY, 3)
    SUB = OperationType("-", Multiplicity.BINARY, 4)
    NEG = OperationType("-", Multiplicity.UNARY, 5)
    MULT = OperationType("*", Multiplicity.BINARY, 6)
    DIV = OperationType("/", Multiplicity.BINARY, 7)
    MOD = OperationType("%", Multiplicity.BINARY, 8)
    ABS = OperationType("|", Multiplicity.UNARY, 9)
    SQRT = OperationType("_/", Multiplicity.UNARY, 10)
    NOP = OperationType("", Multiplicity.UNARY, 11)
