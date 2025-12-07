from dataclasses import dataclass
from enum import Enum, auto

from Types import Condition, JumpType, Operand
from Types.Operations import Operation, OperationType


class InstructionType(Enum):
    A = auto()
    C = auto()


@dataclass
class BaseInstruction:
    line_num: int
    inst_type: InstructionType


class AInstruction(BaseInstruction):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num, InstructionType.A)
        self.value = value

    def __str__(self):
        return f"@{self.value}"


class CInstruction(BaseInstruction):
    def __init__(
        self,
        line_num: int,
        x: Operand,
        y: Operand | None,
        op: OperationType,
        dest: set[Operand] = None,
        jmp: JumpType | None = None,
    ):
        super().__init__(line_num, InstructionType.C)

        self.x = x
        self.y = y
        self.op = op
        self.dest = dest
        if dest is None:
            self.dest = set()
        self.jmp = jmp

    def __str__(self):
        s = f"{self.dest} := " if len(self.dest) > 0 else ""
        s += f"{str(self.op).format(self.x, self.y)}"
        s += (
            f";{f" IF " if self.jmp.condition != Condition.TRUE else ""}{self.jmp.condition.value}{" 0" if self.jmp.condition != Condition.TRUE else ""} JMP A"
            if self.jmp is not None
            else ""
        )
        return s
