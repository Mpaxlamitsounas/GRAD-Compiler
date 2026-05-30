from dataclasses import dataclass

from grad_compiler.Types import JumpType, Operand, OperationType


@dataclass
class BaseInstruction:
    line_num: int

    def copy(self):
        raise NotImplemented

    def __repr__(self):
        raise NotImplemented

    def __str__(self):
        raise NotImplemented


class LabelInstruction(BaseInstruction):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def copy(self):
        return LabelInstruction(self.line_num, self.value)

    def __str__(self):
        return f"({self.value})"

    def __repr__(self):
        return self.__str__()


class AInstruction(BaseInstruction):
    def __init__(self, line_num: int, value: str):
        super().__init__(line_num)
        self.value = value

    def copy(self):
        return AInstruction(self.line_num, self.value)

    def __str__(self):
        return f"@{self.value}"

    def __repr__(self):
        return self.__str__()


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
        super().__init__(line_num)

        self.x = x
        self.y = y
        self.op = op
        self.dest = dest
        if dest is None:
            self.dest: set[Operand] = set()
        self.jmp = jmp

    def copy(self):
        return CInstruction(
            self.line_num,
            self.x,
            self.y,
            self.op,
            self.dest.copy(),
            None if self.jmp is None else self.jmp.copy(),
        )

    def __str__(self):
        s = (
            f"{", ".join([str(d) for d in self.dest])} := "
            if len(self.dest) > 0
            else ""
        )
        s += f"{str(self.op).format(self.x, self.y)}"
        s += f"; {self.jmp}" if self.jmp is not None else ""
        return s

    def __repr__(self):
        return self.__str__()
