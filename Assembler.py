from Types import Condition, JumpType, Operand, OperandType
from Types.Instructions import (
    AInstruction,
    BaseInstruction,
    CInstruction, LabelInstruction,
)
from Types.Operations import Operation
from util import A_register, D_register, M_register, constant_operand

cur_A: int | None = None


def decompress_A_instruction(inst: AInstruction) -> list[BaseInstruction]:
    global cur_A

    cur_A = inst.value
    return [inst]


def _check_instruction_validity(inst: CInstruction) -> bool:
    if any(
        [
            d.type == OperandType.Constant or d.value == "1" or d.value == "2"
            for d in inst.dest
        ]
    ):
        print(f"ERROR Can only assign to registers A, M, or D.")
        raise ValueError

    elif len([dest for dest in inst.dest if dest.value == "M"]) > 1:
        print(f"ERROR Can output to at most one memory location at a time.")
        return False

    return True


def calc_req_A(op: Operand) -> str:
    cur = op.pointer
    loops: int = 0
    try:
        while cur.pointer is not None:
            cur = cur.pointer
            loops += 1
    except AttributeError:
        raise AttributeError

    return "M[" * loops + cur.value + "]" * loops if loops > 0 else cur.value


def _unravel_index(inst: CInstruction, op: Operand) -> list[BaseInstruction]:
    global cur_A

    prev_A = cur_A
    unraveled_instructions: list[BaseInstruction] = []

    cur = op.pointer
    loops: int = 0
    try:
        while cur.pointer is not None:
            unraveled_instructions.append(
                CInstruction(
                    inst.line_num,
                    M_register(None),
                    None,
                    Operation.NOP,
                    {A_register()},
                ),
            )
            cur = cur.pointer
            loops += 1

    except AttributeError:
        raise AttributeError

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
                    inst.line_num, A_register(), None, inst.op, inst.dest, inst.jmp
                )
            )

        case OperandType.Register:
            if inst.x.pointer is None:
                instructions.append(
                    CInstruction(
                        inst.line_num, inst.x, None, inst.op, inst.dest, inst.jmp
                    )
                )

            else:
                instructions.extend(_unravel_index(inst, inst.x))
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        M_register(None),
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
    if (
        inst.x.type == OperandType.Register
        and inst.x.pointer is None
        and inst.y.type == OperandType.Register
        and inst.y.pointer is None
    ):
        instructions.append(inst)
        return

    match inst.x.type, inst.y.type:
        case OperandType.Constant, OperandType.Constant:
            if inst.x.value != cur_A:
                instructions.append(AInstruction(inst.line_num, inst.x.value))

            if inst.x.value != inst.y.value:
                instructions.extend(
                    [
                        CInstruction(
                            inst.line_num,
                            A_register(),
                            None,
                            Operation.NOP,
                            {D_register()},
                        ),
                        AInstruction(inst.line_num, inst.y.value),
                        CInstruction(
                            inst.line_num,
                            D_register(),
                            A_register(),
                            inst.op,
                            inst.dest,
                            inst.jmp,
                        ),
                    ]
                )

            else:
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        A_register(),
                        A_register(),
                        inst.op,
                        inst.dest,
                        inst.jmp,
                    )
                )

            cur_A = inst.y.value

        case OperandType.Constant, OperandType.Register:
            if inst.x.value != cur_A:
                instructions.append(
                    AInstruction(inst.line_num, inst.x.value),
                )
                cur_A = inst.x.value

            if inst.y.pointer is None:
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        A_register(),
                        inst.y,
                        inst.op,
                        inst.dest,
                        inst.jmp,
                    )
                )

            elif cur_A != calc_req_A(inst.y):
                instructions.append(
                    CInstruction(
                        inst.line_num, A_register(), None, Operation.NOP, {D_register()}
                    )
                )

                instructions.extend(_unravel_index(inst, inst.y))
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        D_register(),
                        M_register(None),
                        inst.op,
                        inst.dest,
                        inst.jmp,
                    )
                )

            else:
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        A_register(),
                        M_register(None),
                        inst.op,
                        inst.dest,
                        inst.jmp,
                    )
                )

        case OperandType.Register, OperandType.Constant:
            if inst.y.value != cur_A:
                instructions.append(
                    AInstruction(inst.line_num, inst.y.value),
                )
                cur_A = inst.y.value

            if inst.x.pointer is None:
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        inst.x,
                        A_register(),
                        inst.op,
                        inst.dest,
                        inst.jmp,
                    )
                )

            elif cur_A != calc_req_A(inst.x):
                instructions.append(
                    CInstruction(
                        inst.line_num, A_register(), None, Operation.NOP, {D_register()}
                    )
                )

                instructions.extend(_unravel_index(inst, inst.x))
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        M_register(None),
                        D_register(),
                        inst.op,
                        inst.dest,
                        inst.jmp,
                    )
                )

            else:
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        M_register(None),
                        A_register(),
                        inst.op,
                        inst.dest,
                        inst.jmp,
                    )
                )

        case OperandType.Register, OperandType.Register:
            match inst.x.pointer, inst.y.pointer:
                case _, None:
                    instructions.extend(_unravel_index(inst, inst.x))
                    instructions.append(
                        CInstruction(
                            inst.line_num,
                            M_register(None),
                            inst.y,
                            inst.op,
                            inst.dest,
                            inst.jmp,
                        )
                    )

                case None, _:
                    instructions.extend(_unravel_index(inst, inst.y))
                    instructions.append(
                        CInstruction(
                            inst.line_num,
                            inst.x,
                            M_register(None),
                            inst.op,
                            inst.dest,
                            inst.jmp,
                        )
                    )

                case _, _:
                    if inst.x.pointer != inst.y.pointer:
                        instructions.extend(_unravel_index(inst, inst.x))
                        instructions.append(
                            CInstruction(
                                inst.line_num,
                                M_register(None),
                                None,
                                Operation.NOP,
                                {D_register()},
                            )
                        )

                        instructions.extend(_unravel_index(inst, inst.y))
                        instructions.append(
                            CInstruction(
                                inst.line_num,
                                D_register(),
                                M_register(None),
                                inst.op,
                                inst.dest,
                                inst.jmp,
                            )
                        )

                    else:
                        instructions.extend(_unravel_index(inst, inst.x))
                        instructions.append(
                            CInstruction(
                                inst.line_num,
                                M_register(None),
                                M_register(None),
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

    mem_dests: list[Operand] = [d for d in inst.dest if d.value == "M"]
    mem_dest: Operand = mem_dests[0] if len(mem_dests) != 0 else None
    # memory index in dest
    if mem_dest is not None and mem_dest.pointer is not None:
        last_inst: CInstruction = instructions[-1]
        last_inst.dest.remove(mem_dest)
        last_inst.dest.add(M_register(None))

        if cur_A != calc_req_A(mem_dest):
            del instructions[-1]
            if (
                inst.x.value == "M"
                or inst.x.value == "A"
                or inst.x.type == OperandType.Constant
                or (
                    inst.y is not None
                    and (
                        inst.y.value == "M"
                        or inst.y.value == "A"
                        or inst.y.type == OperandType.Constant
                    )
                )
            ):
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        last_inst.x,
                        last_inst.y,
                        last_inst.op,
                        {D_register()},
                    )
                )

                instructions.extend(_unravel_index(inst, mem_dest))
                instructions.append(
                    CInstruction(
                        inst.line_num,
                        D_register(),
                        None,
                        Operation.NOP,
                        last_inst.dest,
                        inst.jmp,
                    )
                )

            else:
                instructions.extend(_unravel_index(inst, mem_dest))
                instructions.append(last_inst)


def _decompress_jmp_condition_part(
    inst: CInstruction, instructions: list[BaseInstruction]
):
    global cur_A

    if inst.jmp is not None and inst.jmp.compared.value != "0":
        prev_inst: CInstruction = instructions[-1]
        del instructions[-1]

        if len(prev_inst.dest) != 0:
            prev_inst.dest.add(D_register())

            instructions.append(
                CInstruction(
                    inst.line_num,
                    prev_inst.x,
                    prev_inst.y,
                    prev_inst.op,
                    prev_inst.dest,
                ),
            )

        match inst.jmp.compared.type:
            case OperandType.Constant:
                if inst.jmp.compared.value != cur_A:
                    instructions.append(
                        AInstruction(inst.line_num, inst.jmp.compared.value)
                    )
                    cur_A = inst.jmp.compared.value

                instructions.append(
                    CInstruction(
                        inst.line_num,
                        D_register(),
                        A_register(),
                        Operation.SUB,
                        set(),
                        JumpType(
                            prev_inst.jmp.condition,
                            constant_operand("0"),
                            prev_inst.jmp.destination,
                        ),
                    )
                )

            case OperandType.Register:
                if inst.jmp.compared.pointer is None:
                    instructions.append(
                        CInstruction(
                            inst.line_num,
                            D_register(),
                            inst.jmp.compared,
                            Operation.SUB,
                            set(),
                            JumpType(
                                prev_inst.jmp.condition,
                                constant_operand("0"),
                                prev_inst.jmp.destination,
                            ),
                        )
                    )

                else:
                    instructions.extend(_unravel_index(inst, inst.jmp.compared))
                    instructions.append(
                        CInstruction(
                            inst.line_num,
                            D_register(),
                            M_register(None),
                            Operation.SUB,
                            set(),
                            JumpType(
                                prev_inst.jmp.condition,
                                constant_operand("0"),
                                prev_inst.jmp.destination,
                            ),
                        )
                    )


def _decompress_jmp_destination_part(
    inst: CInstruction, instructions: list[BaseInstruction]
):
    global cur_A

    prev_inst: CInstruction = instructions[-1]
    prev_jmp = prev_inst.jmp

    if inst.jmp.destination != cur_A:
        if inst.jmp.condition != Condition.TRUE:
            prev_inst.dest.add(D_register())
        prev_inst.jmp = None

        instructions.extend(
            [
                AInstruction(inst.line_num, prev_jmp.destination),
                CInstruction(
                    inst.line_num, D_register(), None, Operation.NOP, set(), prev_jmp
                ),
            ]
        )
        cur_A = prev_jmp.destination

    instructions[-1].jmp.destination = None


def decompress_C_instruction(inst: CInstruction) -> list[BaseInstruction]:
    if inst.dest is None and inst.jmp is None:
        print(f"INFO Skipping instruction with no effect {inst}")
        return []

    is_valid = _check_instruction_validity(inst)
    if not is_valid:
        raise ValueError

    instructions: list[BaseInstruction] = []

    _decompress_operation_part(inst, instructions)
    _decompress_destination_part(inst, instructions)
    if inst.jmp is not None:
        _decompress_jmp_condition_part(inst, instructions)
        _decompress_jmp_destination_part(inst, instructions)

    return instructions


def decompress_instruction(inst: BaseInstruction) -> list[BaseInstruction]:
    if isinstance(inst, AInstruction):
        return decompress_A_instruction(inst)

    elif isinstance(inst, CInstruction):
        return decompress_C_instruction(inst)

    elif isinstance(inst, LabelInstruction):
        return [inst]

    else:
        return []


def decompress_instructions(
    instructions: list[BaseInstruction],
) -> list[BaseInstruction]:
    decompressed_instructions: list[BaseInstruction] = []
    for inst in instructions:
        decompressed_instructions.extend(decompress_instruction(inst))

    return decompressed_instructions
