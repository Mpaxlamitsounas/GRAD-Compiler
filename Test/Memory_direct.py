from grad.Types import Conditions, JumpType, Operations
from grad.Types.Instructions import CInstruction
from grad.util import D_register, ONE_register
from Test.util import (
    run_test_case,
)


def run_test_cases():
    run_test_case(
        ["M[0]", "M[1]", "M[2]", "M[3]"],
        lambda v: CInstruction(
            0,
            v[1],
            v[2],
            Operations.ADD,
            {v[0]},
            JumpType(Conditions.GE, v[3], "0"),
        ),
        "test_memory_direct_only_memory.txt",
    )

    run_test_case(
        ["M[0]", "M[1]", "M[2]"],
        lambda v: CInstruction(
            0,
            v[1],
            ONE_register,
            Operations.ADD,
            {v[0]},
            JumpType(Conditions.GE, v[2], "0"),
        ),
        "test_memory_direct_with_register.txt",
    )

    run_test_case(
        ["M[0]", "M[1]", "M[2]"],
        lambda v: CInstruction(
            0,
            v[0],
            v[1],
            Operations.ADD,
            {D_register},
            JumpType(Conditions.GE, v[2], "0"),
        ),
        "test_memory_direct_register_dest.txt",
    )

    run_test_case(
        ["M[0]", "M[1]", "M[2]"],
        lambda v: CInstruction(
            0,
            v[1],
            None,
            Operations.NOP,
            {v[0]},
            JumpType(Conditions.GE, v[2], "0"),
        ),
        "test_memory_direct_no_y.txt",
    )
