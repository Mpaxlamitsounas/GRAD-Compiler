from grad_compiler import Context, Options
from grad_compiler.Types import Operand
from grad_compiler.Types.Exceptions import CompilerException
from grad_compiler.Types.Instructions import AInstruction, CInstruction
from grad_compiler.util import (
    A_register,
    D_register,
    ONE_register,
    TWO_register,
    is_M_register,
)


def check_A_inst_validity(inst: AInstruction) -> tuple[bool, str, int | None]:
    if not inst.value.isdigit():
        return False, "A instruction value must be numeric.", None

    if (value := int(inst.value)) < 0:
        return False, "A instruction value must be non negative.", value

    if value > 2**15 - 1:
        return False, "A instruction value must be at most 2^15 - 1.", value

    return True, "", value


def compile_A_instruction(inst: AInstruction) -> bytes:
    return int(inst.value).to_bytes(2, Options.output_instruction_endianness)


def check_C_inst_validity(inst: CInstruction) -> tuple[bool, str]:
    # memory access is not Simple
    memory_operand: list[Operand] = [d for d in inst.dest if is_M_register(d)]
    if any([d.pointer is not None for d in memory_operand]):
        return False, "Memory access must be Simple for compilation."

    # operand does not use build in registers
    for reg in [r for r in [inst.x, inst.y] if r is not None]:
        if reg not in [
            ONE_register,
            TWO_register,
            D_register,
            A_register,
        ] and not is_M_register(reg):
            return False, "Instruction operands must be Simple for compilation."

    if any([r == A_register for r in [inst.x, inst.y]]) and any(
        [is_M_register(reg) for reg in [inst.x, inst.y]]
    ):
        return (
            False,
            "Can not utilise A register and memory at the same time.",
        )

    return True, ""


def compile_C_instruction(inst: CInstruction) -> bytes:
    # flag bit
    value = 0x8000

    # memory bit
    value |= 0x4000 if any([is_M_register(inst.x), is_M_register(inst.y)]) else 0

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

    # operation selection
    value |= inst.op.bit_repr

    return value.to_bytes(2, Options.output_instruction_endianness)


def compile_instruction(instruction: AInstruction | CInstruction) -> bytes:
    if isinstance(instruction, AInstruction):
        is_valid, err_msg, value = check_A_inst_validity(instruction)
        if not is_valid:
            raise CompilerException(instruction.line_num, str(instruction), err_msg)

        inst = compile_A_instruction(instruction)

    elif isinstance(instruction, CInstruction):
        is_valid, err_msg = check_C_inst_validity(instruction)
        if not is_valid:
            raise CompilerException(instruction.line_num, str(instruction), err_msg)

        inst = compile_C_instruction(instruction)

    else:
        raise CompilerException(
            instruction.line_num,
            str(instruction),
            "Instructions to be compiled must either be A or C instructions.",
        )

    return inst


def compile_instructions(
    instructions: list[AInstruction | CInstruction],
) -> list[bytes]:
    compiled_instructions: list[bytes] = []
    for inst in instructions:
        try:
            compiled_instructions.append(compile_instruction(inst))

        except CompilerException as e:
            Context.exceptions.append(e)
            continue

    return compiled_instructions
