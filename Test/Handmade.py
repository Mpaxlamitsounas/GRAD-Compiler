from grad_compiler import Assembler
from grad_compiler.Types import Conditions, JumpType, Operand, OperandType, Operations
from grad_compiler.Types.Instructions import BaseInstruction, CInstruction
from grad_compiler.util import A_register, D_register, ONE_register, constant_operand

from Test.util import (
    write_lines_to_file,
)


def get_test_cases() -> list[BaseInstruction]:
    m0 = Operand(OperandType.Register, "M", constant_operand("0"))
    m1 = Operand(OperandType.Register, "M", constant_operand("1"))
    m2 = Operand(OperandType.Register, "M", constant_operand("2"))
    mm0 = Operand(
        OperandType.Register,
        "M",
        Operand(OperandType.Register, "M", constant_operand("0")),
    )
    mmm0 = Operand(
        OperandType.Register,
        "M",
        Operand(
            OperandType.Register,
            "M",
            Operand(OperandType.Register, "M", constant_operand("0")),
        ),
    )

    return [
        CInstruction(
            0, m0, None, Operations.NOP, {mm0}, JumpType(Conditions.GE, mm0, "0")
        ),
        CInstruction(
            0, mm0, None, Operations.NOP, {m0}, JumpType(Conditions.GE, mm0, "0")
        ),
        CInstruction(
            0, mm0, None, Operations.NOP, {m0}, JumpType(Conditions.GE, m0, "0")
        ),
        CInstruction(
            0,
            constant_operand("1"),
            None,
            Operations.NOP,
            {m0},
            JumpType(Conditions.GE, constant_operand("2"), "1"),
        ),
        CInstruction(
            0, m1, None, Operations.NOP, {m0}, JumpType(Conditions.GE, m2, "2")
        ),
        CInstruction(
            0,
            m0,
            mm0,
            Operations.ADD,
            {mmm0},
            JumpType(Conditions.GE, constant_operand("5"), "0"),
        ),
        CInstruction(0, D_register, ONE_register, Operations.ADD, {A_register}, None),
    ]


def run_test_cases():
    results: list[BaseInstruction | str] = []
    for inst in get_test_cases():
        Assembler.cur_A = None
        results.extend([inst, "---", *Assembler.assemble_instructions([inst]), ""])

    write_lines_to_file("test_handmade.txt", results)
