from dataclasses import dataclass
from enum import Enum, auto


class Multiplicity(Enum):
    NULLARY = 0
    UNARY = 1
    BINARY = 2


@dataclass
class OperationType:
    symbol: str
    multiplicity: Multiplicity

    def __str__(self):
        if self.multiplicity == Multiplicity.NULLARY:
            return ""
        elif self.multiplicity == Multiplicity.UNARY:
            return self.symbol + "{}" + self.symbol
        else:
            return "{} " + self.symbol + " {}"


class Operation:
    ADD = OperationType("+", Multiplicity.BINARY)
    NOP = OperationType("", Multiplicity.UNARY)
