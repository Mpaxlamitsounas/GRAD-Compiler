from grad.Types import Conditions, JumpType, Operations
from grad.Types.Instructions import CInstruction
from grad.util import D_register, ONE_register

from Test.Compiler.util import (
    run_test_case,
)


def run_test_cases():
    run_test_case(
        ["0", "1", "2", "3"],
        lambda v: CInstruction(
            0,
            v[0],
            v[1],
            Operations.ADD,
            {D_register},
            JumpType(Conditions.GE, v[2], v[3].value),
        ),
        "test_constants_only_constants.txt",
    )

    run_test_case(
        ["0", "1", "2"],
        lambda v: CInstruction(
            0,
            v[0],
            ONE_register,
            Operations.ADD,
            {D_register},
            JumpType(Conditions.GE, v[1], v[2].value),
        ),
        "test_constants_with_register.txt",
    )

    run_test_case(
        ["0", "1", "2"],
        lambda v: CInstruction(
            0,
            v[0],
            None,
            Operations.NOP,
            {D_register},
            JumpType(Conditions.GE, v[1], v[2].value),
        ),
        "test_constants_no_y.txt",
    )
