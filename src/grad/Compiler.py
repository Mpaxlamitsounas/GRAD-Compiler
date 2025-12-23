from grad.Types.Instructions import AInstruction, CInstruction
from grad.util import A_register, D_register, ONE_register, TWO_register


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
    return True, ""


def compile_C_inst(inst: CInstruction) -> bytes:
    # flag bit
    value = 0x8000

    # memory bit
    value |= 0x4000 if any([inst.x == A_register(), inst.y == A_register()]) else 0x0000

    # inputs selection
    shift = 0
    for reg in [inst.x, inst.y]:
        if reg is None or reg == ONE_register:
            pass

        elif reg == TWO_register():
            value |= 0x1000 >> shift

        elif reg == D_register():
            value |= 0x2000 >> shift

        elif reg == A_register() or reg.value == "M":
            value |= 0x3000 >> shift

        shift = 2

    # destination selection
    value |= 0x0200 if D_register() in inst.dest else 0
    value |= 0x0100 if A_register() in inst.dest else 0
    value |= 0x0080 if any([d.value == "M" for d in inst.dest]) else 0

    # jmp condition
    if inst.jmp is not None:
        value |= inst.jmp.condition.bit_repr << 4

    # command selection
    value |= inst.op.bit_repr

    return value.to_bytes(2, "big")


def compile_instruction(instruction: AInstruction | CInstruction) -> bytes:
    if isinstance(instruction, AInstruction):
        is_valid, err_msg, value = check_A_inst_validity(instruction)
        if not is_valid:
            raise ValueError(err_msg)

        return compile_A_inst(instruction)

    elif isinstance(instruction, CInstruction):
        is_valid, err_msg = check_C_inst_validity(instruction)
        if not is_valid:
            raise ValueError(err_msg)

        return compile_C_inst(instruction)

    else:
        raise ValueError


def compile_instructions(
    instructions: list[AInstruction | CInstruction],
) -> list[bytes]:
    return [compile_instruction(inst) for inst in instructions]
