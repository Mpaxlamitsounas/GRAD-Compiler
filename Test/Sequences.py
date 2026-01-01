from util import run_test_case_sequence

from grad.Types import Operand, OperandType, Operation
from grad.Types.Instructions import CInstruction
from grad.util import D_register


def run_test_cases():
    run_test_case_sequence(
        [
            CInstruction(0, D_register, None, Operation.NOP, {D_register}, None),
            CInstruction(
                0,
                D_register,
                None,
                Operation.NOP,
                {Operand(OperandType.Register, "M", None)},
                None,
            ),
            CInstruction(
                0,
                D_register,
                None,
                Operation.NOP,
                {Operand(OperandType.Register, "A", None)},
                None,
            ),
        ],
        "test_sequences_optimisations.txt",
    )
