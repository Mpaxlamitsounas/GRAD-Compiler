from grad.Types import Conditions, JumpType, Operations
from grad.Types.Instructions import CInstruction
from grad.util import ONE_register
from Test.util import (
    run_test_case,
)


def run_test_cases():
    run_test_case(
        ["M[M[0]]", "M[M[1]]", "M[M[2]]", "M[M[3]]"],
        lambda v: CInstruction(
            0,
            v[1],
            v[2],
            Operations.ADD,
            {v[0]},
            JumpType(Conditions.GE, v[3], "0"),
        ),
        "test_memory_indirect_only_memory.txt",
    )

    run_test_case(
        ["M[M[0]]", "M[M[1]]", "M[M[2]]"],
        lambda v: CInstruction(
            0,
            v[1],
            ONE_register,
            Operations.ADD,
            {v[0]},
            JumpType(Conditions.GE, v[2], "0"),
        ),
        "test_memory_indirect_with_register.txt",
    )

    run_test_case(
        ["M[M[0]]", "M[M[1]]", "M[M[2]]"],
        lambda v: CInstruction(
            0,
            v[1],
            None,
            Operations.NOP,
            {v[0]},
            JumpType(Conditions.GE, v[2], "0"),
        ),
        "test_memory_indirect_no_y.txt",
    )
