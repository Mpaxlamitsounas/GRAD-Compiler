from grad import Assembler
from grad.Types import Condition, JumpType, Operand, OperandType, Operation
from grad.Types.Instructions import BaseInstruction, CInstruction
from grad.util import A_register, D_register, ONE_register, constant_operand
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
            0, m0, None, Operation.NOP, {mm0}, JumpType(Condition.GE, mm0, "0")
        ),
        CInstruction(
            0, mm0, None, Operation.NOP, {m0}, JumpType(Condition.GE, mm0, "0")
        ),
        CInstruction(
            0, mm0, None, Operation.NOP, {m0}, JumpType(Condition.GE, m0, "0")
        ),
        CInstruction(
            0,
            constant_operand("1"),
            None,
            Operation.NOP,
            {m0},
            JumpType(Condition.GE, constant_operand("2"), "1"),
        ),
        CInstruction(0, m1, None, Operation.NOP, {m0}, JumpType(Condition.GE, m2, "2")),
        CInstruction(
            0,
            m0,
            mm0,
            Operation.ADD,
            {mmm0},
            JumpType(Condition.GE, constant_operand("5"), "0"),
        ),
        CInstruction(0, D_register, ONE_register, Operation.ADD, {A_register}, None),
    ]


def run_test_cases():
    results: list[BaseInstruction | str] = []
    for inst in get_test_cases():
        Assembler.cur_A = None
        results.extend([inst, "---", *Assembler.assemble_instructions([inst]), ""])

    write_lines_to_file("test_handmade.txt", results)
