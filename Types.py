from dataclasses import dataclass
from enum import Enum, auto


class Register(Enum):
    A = "A"
    M = "M"
    D = "D"
    ONE = "1"
    TWO = "2"


@dataclass(frozen=True)
class RegisterArg:
    register: Register
    address: str | None = None

    def __str__(self):
        return self.register.value

    def __repr__(self):
        return self.__str__()


class InstructionType(Enum):
    A = auto()
    C = auto()


class Operation(Enum):
    ADD = "+"
    SUB = "-"
    NOP = ""


class Condition(Enum):
    GE = ">="


@dataclass
class JumpType:
    condition: Condition
    compared: RegisterArg
    destination: str


class Instruction:
    def __init__(self, line_num: int, inst_type: InstructionType):
        self.line_num = line_num
        self.inst_type = inst_type


class AInstruction(Instruction):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num, InstructionType.A)
        self.value = value

    def __str__(self):
        return f"@{self.value}"


class CInstruction(Instruction):
    def __init__(
        self,
        line_num: int,
        x: RegisterArg,
        y: RegisterArg | None,
        op: Operation,
        dest: set[RegisterArg] = None,
        jmp: JumpType | None = None,
    ):
        super().__init__(line_num, InstructionType.C)

        self.x = x
        self.y = y
        self.op = op
        if dest is None:
            self.dest = set()
        else:
            self.dest = dest
        self.jmp = jmp

    def __str__(self):
        return f"{f"{self.dest} = " if len(self.dest) > 0 else ""}{self.x} {self.op.value}{f" {self.y} " if self.y is not None else ""}{f"; IF {self.jmp.condition.value} 0 JMP A" if self.jmp is not None else ""}"
