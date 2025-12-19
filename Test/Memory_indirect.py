from grad.Types import Condition, JumpType
from grad.Types.Instructions import CInstruction
from grad.Types.Operations import Operation
from grad.util import ONE_register
from Test.util import (
    test_case,
)


def run_test_cases():
    test_case(
        ["M[M[0]]", "M[M[1]]", "M[M[2]]", "M[M[3]]"],
        lambda v: CInstruction(
            0,
            v[1],
            v[2],
            Operation.ADD,
            {v[0]},
            JumpType(Condition.GE, v[3], "0"),
        ),
        "test_memory_indirect_only_memory.txt",
    )

    test_case(
        ["M[M[0]]", "M[M[1]]", "M[M[2]]"],
        lambda v: CInstruction(
            0,
            v[1],
            ONE_register(),
            Operation.ADD,
            {v[0]},
            JumpType(Condition.GE, v[2], "0"),
        ),
        "test_memory_indirect_with_register.txt",
    )

    test_case(
        ["M[M[0]]", "M[M[1]]", "M[M[2]]"],
        lambda v: CInstruction(
            0,
            v[1],
            None,
            Operation.NOP,
            {v[0]},
            JumpType(Condition.GE, v[2], "0"),
        ),
        "test_memory_indirect_no_y.txt",
    )
