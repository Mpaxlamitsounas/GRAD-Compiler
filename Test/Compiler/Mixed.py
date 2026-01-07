from grad.Types import Conditions, JumpType, Operand, OperandType, Operations
from grad.Types.Instructions import CInstruction
from Test.Compiler.util import (
    run_test_case,
)


def run_test_cases():
    run_test_case(
        ["M[M[0]]", "M[2]", "3"],
        lambda v: CInstruction(
            0,
            v[0],
            v[1],
            Operations.ADD,
            {Operand(OperandType.Register, "M", Operand(OperandType.Constant, "1"))},
            JumpType(Conditions.GE, v[2], "0"),
        ),
        "test_mixed_M_dest_no_dup.txt",
    )

    run_test_case(
        ["M[M[0]]", "M[1]", "0"],
        lambda v: CInstruction(
            0,
            v[0],
            v[1],
            Operations.ADD,
            {Operand(OperandType.Register, "M", Operand(OperandType.Constant, "1"))},
            JumpType(Conditions.GE, v[2], "0"),
        ),
        "test_mixed_M_dest_yes_dup_1.txt",
    )

    run_test_case(
        ["3", "M[1]", "3"],
        lambda v: CInstruction(
            0,
            v[0],
            v[1],
            Operations.ADD,
            {Operand(OperandType.Register, "M", Operand(OperandType.Constant, "1"))},
            JumpType(Conditions.GE, v[2], "0"),
        ),
        "test_mixed_M_dest_yes_dup_2.txt",
    )
