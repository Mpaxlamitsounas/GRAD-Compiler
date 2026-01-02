from typing import TextIO

from grad import Context, Options
from grad.Types import (
    Conditions,
    JumpType,
    Multiplicity,
    Operand,
    OperandType,
    Operations,
)
from grad.Types.Exceptions import AssemblerException
from grad.Types.Instructions import (
    AInstruction,
    BaseInstruction,
    CInstruction,
    LabelInstruction,
)
from grad.util import (
    A_register,
    D_register,
    M_simple_register,
    ONE_register,
    TWO_register,
    constant_operand,
    is_M_register,
)

# None represents unknown
cur_A: str | None = None


def decompress_A_instruction(inst: AInstruction) -> list[BaseInstruction]:
    global cur_A

    inst.value = Context.symbols.get(inst.value, inst.value)

    cur_A = inst.value
    return [inst.copy()]


def check_inst_validity(inst: CInstruction) -> tuple[bool, str]:
    if any(
        [
            d.type == OperandType.Constant or d == ONE_register or d == TWO_register
            for d in inst.dest
        ]
    ):
        return False, "Can only assign to registers A, M, or D."

    if len([d for d in inst.dest if is_M_register(d)]) > 1:
        return False, "Can output to at most one memory location at a time."

    if any([A_register == inst.x, A_register == inst.y]) and any(
        [is_M_register(inst.x), inst.y is not None and is_M_register(inst.y)]
    ):
        return False, "Can not utilise A register and memory at the same time."

    return True, ""


def calc_req_A(op: Operand) -> str:
    cur = op.pointer
    loops: int = 0
    while cur.pointer is not None:
        cur = cur.pointer
        loops += 1

    return "M[" * loops + cur.value + "]" * loops if loops > 0 else cur.value


def _unravel_index(inst: CInstruction, op: Operand) -> list[BaseInstruction]:
    global cur_A

    prev_A = cur_A
    unraveled_instructions: list[BaseInstruction] = []

    cur = op.pointer
    loops: int = 0
    while cur.pointer is not None:
        unraveled_instructions.append(
            CInstruction(
                inst.line_num,
                M_simple_register,
                None,
                Operations.NOP,
                {A_register},
            ),
        )
        cur = cur.pointer
        loops += 1

    if loops > 0:
        cur_A = "M[" * loops + cur.value + "]" * loops

    if cur.value != prev_A:
        unraveled_instructions.append(AInstruction(inst.line_num, cur.value))
        cur_A = cur.value if loops == 0 else cur_A

    unraveled_instructions.reverse()
    return unraveled_instructions


def _decompress_unary_operation(
    inst: CInstruction, instructions: list[BaseInstruction]
):
    global cur_A

    # instruction has already been decompressed
    if inst.x.type == OperandType.Register and inst.x.pointer is None:
        instructions.append(inst)
        return

    match inst.x.type:
        case OperandType.Constant:
            if inst.x.value != cur_A:
                instructions.append(AInstruction(inst.line_num, inst.x.value))
                cur_A = inst.x.value

            instructions.append(
                CInstruction(
                    inst.line_num, A_register, None, inst.op, inst.dest, inst.jmp
                )
            )

        case OperandType.Register:
            if inst.x.pointer is None:
                x_reg = inst.x

            else:
                x_reg = M_simple_register
                instructions.extend(_unravel_index(inst, inst.x))

            instructions.append(
                CInstruction(
                    inst.line_num,
                    x_reg,
                    None,
                    inst.op,
                    inst.dest,
                    inst.jmp,
                )
            )


def _decompress_binary_operation(
    inst: CInstruction, instructions: list[BaseInstruction]
):
    global cur_A

    # instruction has already been decompressed
    if all(
        [
            all([reg.type == OperandType.Register, reg.pointer is None])
            for reg in [inst.x, inst.y]
        ]
    ):
        instructions.append(inst)
        return

    match inst.x.type, inst.y.type:
        case OperandType.Constant, OperandType.Constant:
            if inst.x.value != cur_A:
                instructions.append(AInstruction(inst.line_num, inst.x.value))

            if inst.x.value != inst.y.value:
                x_reg = D_register
                instructions.extend(
                    [
                        CInstruction(
                            inst.line_num,
                            A_register,
                            None,
                            Operations.NOP,
                            {D_register},
                        ),
                        AInstruction(inst.line_num, inst.y.value),
                    ]
                )

            else:
                x_reg = A_register

            instructions.append(
                CInstruction(
                    inst.line_num,
                    x_reg,
                    A_register,
                    inst.op,
                    inst.dest,
                    inst.jmp,
                )
            )

            cur_A = inst.y.value

        case OperandType.Register, OperandType.Constant:
            if inst.y.value != cur_A:
                instructions.append(
                    AInstruction(inst.line_num, inst.y.value),
                )

                cur_A = inst.y.value

            if inst.x.pointer is None:
                x_reg, y_reg = inst.x, A_register

            elif cur_A == calc_req_A(inst.x):
                x_reg, y_reg = M_simple_register, A_register

            else:
                x_reg, y_reg = M_simple_register, D_register
                instructions.append(
                    CInstruction(
                        inst.line_num, A_register, None, Operations.NOP, {D_register}
                    )
                )

                instructions.extend(_unravel_index(inst, inst.x))

            instructions.append(
                CInstruction(
                    inst.line_num,
                    x_reg,
                    y_reg,
                    inst.op,
                    inst.dest,
                    inst.jmp,
                )
            )

        # most operations are commutative, but NEG is not, so this is needed
        case OperandType.Constant, OperandType.Register:
            if inst.x.value != cur_A:
                instructions.append(
                    AInstruction(inst.line_num, inst.x.value),
                )

                cur_A = inst.x.value

            if inst.y.pointer is None:
                x_reg, y_reg = A_register, inst.y

            elif cur_A == calc_req_A(inst.y):
                x_reg, y_reg = A_register, M_simple_register

            else:
                x_reg, y_reg = D_register, M_simple_register
                instructions.append(
                    CInstruction(
                        inst.line_num, A_register, None, Operations.NOP, {D_register}
                    )
                )

                instructions.extend(_unravel_index(inst, inst.y))

            instructions.append(
                CInstruction(
                    inst.line_num,
                    x_reg,
                    y_reg,
                    inst.op,
                    inst.dest,
                    inst.jmp,
                )
            )

        case OperandType.Register, OperandType.Register:
            match inst.x.pointer, inst.y.pointer:
                case _, None:
                    x_reg, y_reg, unravel_reg = M_simple_register, inst.y, inst.x

                case None, _:
                    x_reg, y_reg, unravel_reg = inst.x, M_simple_register, inst.y

                case _, _:
                    if inst.x.pointer != inst.y.pointer:
                        instructions.extend(_unravel_index(inst, inst.x))
                        instructions.append(
                            CInstruction(
                                inst.line_num,
                                M_simple_register,
                                None,
                                Operations.NOP,
                                {D_register},
                            )
                        )

                        x_reg, y_reg, unravel_reg = (
                            D_register,
                            M_simple_register,
                            inst.y,
                        )

                    else:
                        x_reg, y_reg, unravel_reg = (
                            M_simple_register,
                            M_simple_register,
                            inst.x,
                        )

            # x_reg, y_reg, and unravel_reg are assigned in all cases
            # noinspection PyUnboundLocalVariable
            instructions.extend(_unravel_index(inst, unravel_reg))
            # noinspection PyUnboundLocalVariable
            instructions.append(
                CInstruction(
                    inst.line_num,
                    x_reg,
                    y_reg,
                    inst.op,
                    inst.dest,
                    inst.jmp,
                )
            )


def _decompress_operation_part(inst: CInstruction, instructions: list[BaseInstruction]):
    if inst.y is None:
        _decompress_unary_operation(inst, instructions)
    else:
        _decompress_binary_operation(inst, instructions)


def _decompress_destination_part(
    inst: CInstruction, instructions: list[BaseInstruction]
):
    global cur_A

    mem_dests: list[Operand] = [d for d in inst.dest if is_M_register(d)]
    # guaranteed to be only 1 from previous check
    mem_dest: Operand = mem_dests[0] if len(mem_dests) != 0 else None

    # memory index in dest
    if mem_dest is not None and mem_dest.pointer is not None:
        # Every decompress step caps the instruction list with a C inst
        # noinspection PyTypeChecker
        last_inst: CInstruction = instructions[-1]
        last_inst.dest.remove(mem_dest)
        last_inst.dest.add(M_simple_register)

        if cur_A != calc_req_A(mem_dest):
            del instructions[-1]
            # inst utilises A or M registers in computation
            if any(
                any(
                    [
                        is_M_register(reg),
                        reg == A_register,
                        reg.type == OperandType.Constant,
                    ]
                )
                for reg in [inst.x, inst.y]
                if reg is not None
            ):
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        last_inst.x,
                        last_inst.y,
                        last_inst.op,
                        {D_register},
                    )
                )

                instructions.extend(_unravel_index(inst, mem_dest))
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        D_register,
                        None,
                        Operations.NOP,
                        last_inst.dest,
                        inst.jmp,
                    )
                )

            else:
                instructions.extend(_unravel_index(inst, mem_dest))
                instructions.append(last_inst)

    if A_register in inst.dest:
        cur_A = None


def _decompress_jmp_condition_part(
    inst: CInstruction, instructions: list[BaseInstruction]
):
    global cur_A

    if inst.jmp is not None and inst.jmp.compared.value != "0":
        # Every decompress step caps the instruction list with a C inst
        # noinspection PyTypeChecker
        prev_inst: CInstruction = instructions[-1]

        prev_inst.dest.add(D_register)

        match inst.jmp.compared.type:
            case OperandType.Constant:
                if inst.jmp.compared.value != cur_A:
                    instructions.append(
                        AInstruction(inst.line_num, inst.jmp.compared.value),
                    )

                    cur_A = inst.jmp.compared.value

                x_reg, y_reg = D_register, A_register

            case OperandType.Register:
                if inst.jmp.compared.pointer is not None:
                    if cur_A != calc_req_A(prev_inst.jmp.compared):
                        instructions.extend(_unravel_index(inst, inst.jmp.compared))

                    x_reg, y_reg = D_register, M_simple_register

                else:
                    x_reg, y_reg = D_register, inst.jmp.compared

        # assigned in all cases
        # noinspection PyUnboundLocalVariable
        instructions.append(
            CInstruction(
                inst.line_num,
                x_reg,
                y_reg,
                Operations.SUB,
                set(),
                JumpType(
                    prev_inst.jmp.condition,
                    constant_operand("0"),
                    prev_inst.jmp.destination,
                ),
            ),
        )

        prev_inst.jmp = None


def _decompress_jmp_destination_part(
    inst: CInstruction, instructions: list[BaseInstruction]
):
    global cur_A

    # Every decompress step caps the instruction list with a C inst
    # noinspection PyTypeChecker
    prev_inst: CInstruction = instructions[-1]
    prev_jmp = prev_inst.jmp

    if inst.jmp.destination != cur_A and inst.jmp.destination is not None:
        if inst.jmp.condition != Conditions.TRUE:
            prev_inst.dest.add(D_register)

        if len(prev_inst.dest) > 0:
            prev_inst.jmp = None
        else:
            del instructions[-1]

        instructions.extend(
            [
                AInstruction(inst.line_num, prev_jmp.destination),
                CInstruction(
                    inst.line_num, D_register, None, Operations.NOP, set(), prev_jmp
                ),
            ]
        )

        cur_A = prev_jmp.destination

    # guaranteed to be C inst since extend is right above
    # noinspection PyUnresolvedReferences
    instructions[-1].jmp.destination = None


def decompress_C_instruction(inst: CInstruction) -> list[BaseInstruction]:
    if len(inst.dest) == 0 and inst.jmp is None:
        print(f'Skipping instruction with no effect "{inst}".')
        return []

    is_valid, err_msg = check_inst_validity(inst)
    if not is_valid:
        raise AssemblerException(inst.line_num, str(inst), err_msg)

    inst = inst.copy()
    instructions: list[BaseInstruction] = []

    if inst.op.multiplicity == Multiplicity.UNARY:
        inst.y = None

    _decompress_operation_part(inst, instructions)
    _decompress_destination_part(inst, instructions)
    if inst.jmp is not None:
        _decompress_jmp_condition_part(inst, instructions)
        _decompress_jmp_destination_part(inst, instructions)

    return instructions


def decompress_Label_instruction(
    instruction: LabelInstruction,
) -> list[BaseInstruction]:
    global cur_A

    cur_A = None
    return [instruction.copy()]


def decompress_instruction(instruction: BaseInstruction) -> list[BaseInstruction]:
    if isinstance(instruction, AInstruction):
        return decompress_A_instruction(instruction)

    elif isinstance(instruction, CInstruction):
        return decompress_C_instruction(instruction)

    elif isinstance(instruction, LabelInstruction):
        return decompress_Label_instruction(instruction)

    else:
        return []


def decompress_instructions(
    instructions: list[BaseInstruction],
) -> list[BaseInstruction]:
    decompressed_instructions: list[BaseInstruction] = []
    for inst in instructions:
        decompressed_instructions.extend(decompress_instruction(inst))

    return decompressed_instructions


def substitute_jump_labels(
    instructions: list[BaseInstruction],
) -> list[AInstruction | CInstruction]:
    labels: dict[str, str] = {}
    cnt = 0
    for idx, inst in enumerate(instructions.copy()):
        if isinstance(inst, LabelInstruction):
            labels[inst.value] = str(idx - cnt)
            cnt += 1
            instructions.remove(inst)

    for inst in instructions:
        if isinstance(inst, AInstruction):
            if inst.value in labels:
                inst.value = labels[inst.value]

            elif not inst.value.isdigit():
                raise AssemblerException(
                    inst.line_num,
                    str(inst),
                    "A instruction value must be numeric or a numeric alias.",
                )

    # no BaseInstruction instances are ever added, and all LabelInstruction instances are removed here
    # noinspection PyTypeChecker
    return instructions


def _optimise_C_inst_dest_merge(
    instructions: list[BaseInstruction],
) -> list[BaseInstruction]:
    if len(instructions) < 2:
        return instructions

    optim_instructions: list[BaseInstruction] = [instructions[0]]
    prev_inst = instructions[0]
    for cur_inst in instructions[1:]:
        if (
            isinstance(prev_inst, CInstruction)
            and isinstance(cur_inst, CInstruction)
            and all(  # identical comp part and no dependencies
                [
                    prev_inst.x == cur_inst.x,
                    prev_inst.y == cur_inst.y,
                    prev_inst.op == cur_inst.op,
                    prev_inst.jmp is None,
                    cur_inst.x not in prev_inst.dest,
                    cur_inst.y not in prev_inst.dest,
                ]
            )  # no memory dependencies
            and (
                A_register not in prev_inst.dest
                or (
                    not is_M_register(cur_inst.x)
                    and (
                        not is_M_register(cur_inst.y)
                        if cur_inst.y is not None
                        else True
                    )
                    and all([not is_M_register(d) for d in cur_inst.dest])
                )
            )
        ):
            prev_inst.dest = prev_inst.dest | cur_inst.dest
            prev_inst.jmp = cur_inst.jmp
            continue

        optim_instructions.append(cur_inst)
        prev_inst = cur_inst

    return optim_instructions


def _optimise_C_inst_redundant_A_assign_make_inline(
    instructions: list[BaseInstruction],
) -> list[BaseInstruction]:
    if len(instructions) < 2:
        return instructions

    optim_instructions: list[BaseInstruction] = [instructions[0]]
    prev_inst = instructions[0]
    for cur_inst in instructions[1:]:
        if (
            isinstance(prev_inst, CInstruction)
            and isinstance(cur_inst, CInstruction)
            and all(
                [
                    prev_inst.x == A_register,
                    prev_inst.op == Operations.NOP,
                    prev_inst.jmp is None,
                    prev_inst.dest == {D_register},
                    cur_inst.op != Operations.NOP,
                    cur_inst.x == D_register or cur_inst.y == D_register,
                ]
            )
        ):
            del optim_instructions[-1]
            if cur_inst.x == D_register:
                cur_inst.x = A_register
            else:
                cur_inst.y = A_register

        optim_instructions.append(cur_inst)
        prev_inst = cur_inst

    return optim_instructions


def _optimise_C_inst_remove_self_assign(
    instructions: list[BaseInstruction],
) -> list[BaseInstruction]:
    if len(instructions) == 0:
        return []

    optim_instructions: list[BaseInstruction] = []
    for inst in instructions:
        if isinstance(inst, CInstruction) and all(
            [
                all([inst.x == d for d in inst.dest]),
                inst.y is None,
                inst.op == Operations.NOP,
            ]
        ):
            if inst.jmp is None:
                continue
            else:
                inst.dest = {}

        optim_instructions.append(inst)

    return optim_instructions


def _optimise_A_inst_unused_A_load(
    instructions: list[BaseInstruction],
) -> list[BaseInstruction]:
    if len(instructions) < 2:
        return instructions

    optim_instructions: list[BaseInstruction] = [instructions[0]]
    prev_inst = instructions[0]
    for cur_inst in instructions[1:]:
        if isinstance(prev_inst, AInstruction) and isinstance(cur_inst, AInstruction):
            del optim_instructions[-1]

        optim_instructions.append(cur_inst)
        prev_inst = cur_inst

    return optim_instructions


def apply_optimisations(instructions: list[BaseInstruction]) -> list[BaseInstruction]:
    instructions = _optimise_C_inst_dest_merge(instructions)
    instructions = _optimise_C_inst_redundant_A_assign_make_inline(instructions)
    instructions = _optimise_C_inst_remove_self_assign(instructions)
    instructions = _optimise_A_inst_unused_A_load(instructions)

    return instructions


def assemble_instructions(
    instructions: list[BaseInstruction], output_file: TextIO | None = None
) -> list[AInstruction | CInstruction]:
    instructions = decompress_instructions(instructions)
    if Options.apply_post_optimisations:
        instructions = apply_optimisations(instructions)
    instructions = substitute_jump_labels(instructions)

    if output_file is not None:
        output_file.writelines([f"{inst}\n" for inst in instructions])

    return instructions
