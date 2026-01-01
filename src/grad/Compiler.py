from typing import BinaryIO

from grad.Types import Operand
from grad.Types.Instructions import AInstruction, CInstruction
from grad.util import A_register, D_register, ONE_register, TWO_register, is_M_register


def check_A_inst_validity(inst: AInstruction) -> tuple[bool, str, int | None]:
    if not inst.value.isdigit():
        return False, "TODO", None

    value = int(inst.value)
    if value < 0:
        return False, "TODO", value

    if value > 2**15 - 1:
        return False, "TODO", value

    return True, "", value


def compile_A_inst(inst: AInstruction) -> bytes:
    return int(inst.value).to_bytes(2, "big")


def check_C_inst_validity(inst: CInstruction) -> tuple[bool, str]:
    # memory access is not Simple
    memory_operand: list[Operand] = [d for d in inst.dest if is_M_register(d)]
    if any([d.pointer is not None for d in memory_operand]):
        return False, ""

    # operand does not use build in registers
    for reg in [r for r in [inst.x, inst.y] if r is not None]:
        if reg not in [
            ONE_register,
            TWO_register,
            D_register,
            A_register,
        ] and not is_M_register(reg):
            return False, ""

    return True, ""


def compile_C_inst(inst: CInstruction) -> bytes:
    # flag bit
    value = 0x8000

    # memory bit
    value |= 0x4000 if not any([inst.x == A_register, inst.y == A_register]) else 0x0000

    # inputs selection
    shift = 0
    for reg in [inst.x, inst.y]:
        if reg is None or reg == ONE_register:
            pass

        elif reg == TWO_register:
            value |= 0x1000 >> shift

        elif reg == D_register:
            value |= 0x2000 >> shift

        elif reg == A_register or is_M_register(reg):
            value |= 0x3000 >> shift

        shift = 2

    # destination selection
    value |= 0x0200 if D_register in inst.dest else 0
    value |= 0x0100 if A_register in inst.dest else 0
    value |= 0x0080 if any([is_M_register(d) for d in inst.dest]) else 0

    # jmp condition
    if inst.jmp is not None:
        value |= inst.jmp.condition.bit_repr << 4

    # command selection
    value |= inst.op.bit_repr

    return value.to_bytes(2, "big")


def compile_instruction(instruction: AInstruction | CInstruction, output_file: BinaryIO | None = None) -> bytes:
    if isinstance(instruction, AInstruction):
        is_valid, err_msg, value = check_A_inst_validity(instruction)
        if not is_valid:
            raise ValueError(err_msg)

        inst = compile_A_inst(instruction)

    elif isinstance(instruction, CInstruction):
        is_valid, err_msg = check_C_inst_validity(instruction)
        if not is_valid:
            raise ValueError(err_msg)

        inst = compile_C_inst(instruction)

    else:
        raise ValueError

    if output_file is not None:
        output_file.write(f"{inst}\n")

    return inst


def compile_instructions(
    instructions: list[AInstruction | CInstruction],
    output_file: BinaryIO | None = None
) -> list[bytes]:
    return [compile_instruction(inst, output_file) for inst in instructions]
