from grad.Types import Condition, JumpType
from grad.Types.Instructions import CInstruction
from grad.Types.Operations import Operation
from grad.util import D_register, ONE_register
from Test.util import (
    test_case,
)


def run_test_cases():
    test_case(
        ["0", "1", "2", "3"],
        lambda v: CInstruction(
            0,
            v[0],
            v[1],
            Operation.ADD,
            {D_register()},
            JumpType(Condition.GE, v[2], v[3].value),
        ),
        "test_constants_only_constants.txt",
    )

    test_case(
        ["0", "1", "2"],
        lambda v: CInstruction(
            0,
            v[0],
            ONE_register(),
            Operation.ADD,
            {D_register()},
            JumpType(Condition.GE, v[1], v[2].value),
        ),
        "test_constants_with_register.txt",
    )

    test_case(
        ["0", "1", "2"],
        lambda v: CInstruction(
            0,
            v[0],
            None,
            Operation.NOP,
            {D_register()},
            JumpType(Condition.GE, v[1], v[2].value),
        ),
        "test_constants_no_y.txt",
    )
