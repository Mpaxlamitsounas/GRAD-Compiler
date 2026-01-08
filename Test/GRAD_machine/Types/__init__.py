from dataclasses import dataclass
from enum import IntFlag


class ALUFlags(IntFlag):
    zx = 0b10000000
    nx = 0b01000000
    zy = 0b00100000
    ny = 0b00010000
    no = 0b00000001
    AND = 0b00000000
    OR = nx | ny | AND | no
    NOT = nx | zy | ny | AND
    ADD = 0b00000010
    SUB = nx | ADD | no
    NEG = zy | ny | ADD | no
    MULT = 0b00000100
    DIV = 0b00000110
    MOD = 0b00001000
    ABS = 0b00001010
    SQRT = 0b00001100
    NOP = ny | zy | AND
    XOR = 0b00001110
    NONE = 0b00000000

    def to_ALU_input(self) -> str:
        s = format(self.value, "08b")
        return "  ".join([s[0], s[1], s[2], s[3], f"0b{s[4:7]}", s[7]])


@dataclass
class ALUCase:
    x: int
    y: int
    out: int
    flags: ALUFlags
