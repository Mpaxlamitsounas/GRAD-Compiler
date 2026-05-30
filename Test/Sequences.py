from grad_compiler.Types import Operand, OperandType, Operations
from grad_compiler.Types.Instructions import CInstruction
from grad_compiler.util import D_register
from util import run_test_case_sequence


def run_test_cases():
    run_test_case_sequence(
        [
            CInstruction(0, D_register, None, Operations.NOP, {D_register}, None),
            CInstruction(
                0,
                D_register,
                None,
                Operations.NOP,
                {Operand(OperandType.Register, "M", None)},
                None,
            ),
            CInstruction(
                0,
                D_register,
                None,
                Operations.NOP,
                {Operand(OperandType.Register, "A", None)},
                None,
            ),
        ],
        "test_sequences_optimisations.txt",
    )
