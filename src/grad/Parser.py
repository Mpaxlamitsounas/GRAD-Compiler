from grad import Context
from grad.Types import Condition, JumpType, Operand, OperandType, Operation
from grad.Types.Instructions import (
    AInstruction,
    BaseInstruction,
    CInstruction,
    LabelInstruction,
)
from grad.util import constant_operand, strip_and_filter_all


def parse_operand(operand: str) -> Operand:
    if " " in operand or operand == "":
        raise ValueError

    if not operand.isalnum() and operand[0] != "M":
        raise ValueError

    if operand in Context.reserved:
        raise ValueError

    elif any(
        [operand == "D", operand == "A", operand == "1", operand == "2", operand == "M"]
    ):
        return Operand(OperandType.Register, operand)

    elif operand.startswith("M[") and operand.endswith("]"):
        operand = parse_operand(operand[2:-1])
        return Operand(OperandType.Register, "M", operand)

    elif operand in Context.symbols:
        return parse_operand(Context.symbols[operand])

    else:
        return Operand(OperandType.Constant, operand)


def parse_instructions(
    file: list[str],
) -> list[BaseInstruction] | list[AInstruction | CInstruction]:
    instructions: list[BaseInstruction] = []
    line_num: int = 0

    for line in file:
        # A-Instruction
        if "@" in line:
            instructions.append(AInstruction(line_num, line[1:].strip()))

        # Alias
        elif ":" in line and ":=" not in line:
            split = strip_and_filter_all(line.split(":"))
            if len(split) != 2:
                raise ValueError

            Context.symbols[split[0]] = split[1]

        # Jump label
        elif line.startswith("("):
            name = line[1:-1]
            if len(name) == 0:
                raise ValueError

            instructions.append(LabelInstruction(line_num, name))

        # Variable
        elif line.startswith("VAR "):
            name = line.replace("VAR ", "").strip()
            if line == "":
                raise ValueError

            Context.symbols[name] = f"M[{Context.available_RAM.pop()}]"

        # C-Instruction
        else:
            # dest = rest
            if ":=" in line:
                dest, rest = line.split(":=")

            else:
                dest, rest = None, line

            # operation ; jmp
            if ";" in rest:
                operation_str, jmp = rest.split(";")
                jmp = jmp.replace("IF", "")

            else:
                jmp = None
                operation_str = rest

            # operand operation operand
            if "&" in operation_str:
                operation = Operation.AND

            elif "|" in operation_str:
                parts = strip_and_filter_all(operation_str.split("|"))
                operation = Operation.OR if len(parts) == 2 else Operation.ABS

            elif "~" in operation_str:
                operation = Operation.NOT

            elif "+" in operation_str:
                operation = Operation.ADD

            elif "-" in operation_str:
                parts = strip_and_filter_all(operation_str.split("-"))
                operation = Operation.SUB if len(parts) == 2 else Operation.NEG

            elif "*" in operation_str:
                operation = Operation.MULT

            elif "/" in operation_str and "_" not in operation_str:
                operation = Operation.DIV

            elif "%" in operation_str:
                operation = Operation.MOD

            elif "_/" in operation_str:
                operation = Operation.SQRT

            else:
                operation = Operation.NOP

            try:
                operands = strip_and_filter_all(operation_str.split(operation.symbol))
            # empty separator (NOP)
            except ValueError:
                operands = (
                    [operation_str.strip()] if operation_str.strip() != "" else []
                )

            if len(operands) != operation.multiplicity.value:
                raise ValueError

            else:
                x, y = parse_operand(operands[0]), (
                    parse_operand(operands[1]) if len(operands) != 1 else None
                )

            if dest is not None:
                dest = {parse_operand(d) for d in strip_and_filter_all(dest.split(","))}

            if jmp is not None:
                jmp = strip_and_filter_all(jmp.split("JMP"))

                match len(jmp):
                    # compatibility case (already parsed)
                    case 0:
                        jmp = JumpType(Condition.TRUE, constant_operand("0"), None)

                    case 1:
                        jmp = strip_and_filter_all(jmp[0].split())
                        match len(jmp):
                            case 1:
                                jmp = JumpType(
                                    Condition.TRUE, constant_operand("0"), jmp[0]
                                )

                            case 2:
                                jmp = JumpType(
                                    Condition.get_from_value(jmp[0]),
                                    parse_operand(jmp[1]),
                                    None,
                                )

                    case 2:
                        jmp_dest = jmp[1]
                        try:
                            jmp_cond, jmp_oper = strip_and_filter_all(jmp[0].split())
                        except:
                            raise ValueError

                        jmp = JumpType(
                            Condition.get_from_value(jmp_cond),
                            parse_operand(jmp_oper),
                            jmp_dest,
                        )

                    case _:
                        raise ValueError

            instructions.append(CInstruction(line_num, x, y, operation, dest, jmp))

        line_num += 1

    return instructions
