from grad_compiler import Context
from grad_compiler.Types import Conditions, JumpType, Operand, OperandType, Operations
from grad_compiler.Types.Exceptions import ParserException
from grad_compiler.Types.Instructions import (
    AInstruction,
    BaseInstruction,
    CInstruction,
    LabelInstruction,
)
from grad_compiler.util import constant_operand, filter_all, is_valid_identifier_name

line_num: int = 0
cur_line: str = ""


def parse_operand(operand: str) -> Operand:
    if operand == "":
        raise ParserException(line_num, cur_line, "Tried to parse empty operand.")

    if operand[0] == "-":
        raise ParserException(
            line_num,
            cur_line,
            "Values must be non negative, to introduce a negative value use the negation operation.",
        )

    if not is_valid_identifier_name(operand):
        raise ParserException(
            line_num,
            cur_line,
            f'Identifier "{operand}" contains disallowed characters (charset is [A-Z_]).',
        )

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


def parse_A_instruction(line: str) -> AInstruction:
    value = line[1:]
    if value == "":
        raise ParserException(
            line_num, cur_line, "A instruction must have non-empty value."
        )

    if not is_valid_identifier_name(value):
        raise ParserException(
            line_num,
            cur_line,
            f'Identifier "{value}" contains disallowed characters (charset is [A-Z_]).',
        )

    return AInstruction(line_num, value)


def parse_alias(line: str):
    split = line.split(":")
    if len(split) != 2:
        raise ParserException(
            line_num,
            cur_line,
            f'Alias declaration missing name or value, or has too many ":" (NAME:VALUE).',
        )

    for name in split:
        if not is_valid_identifier_name(name):
            raise ParserException(
                line_num,
                cur_line,
                f'Identifier "{name}" contains disallowed characters (charset is [A-Z_]).',
            )

    Context.symbols[split[0]] = split[1]


def parse_jump_label(line: str) -> LabelInstruction:
    name = line[1:-1]
    if name == "":
        raise ParserException(
            line_num, cur_line, "Jump labels must have non-empty name."
        )

    if not is_valid_identifier_name(name):
        raise ParserException(
            line_num,
            cur_line,
            f'Identifier "{name}" contains disallowed characters (charset is [A-Z_]).',
        )

    return LabelInstruction(line_num, name)


def parse_variable(line: str):
    name = line.replace("VAR", "", 1)
    if line == "":
        raise ParserException(
            line_num, cur_line, "Variable declarations must have non-empty name."
        )

    if not is_valid_identifier_name(name):
        raise ParserException(
            line_num,
            cur_line,
            f'Identifier "{name}" contains disallowed characters (charset is [A-Z_]).',
        )

    try:
        Context.symbols[name] = f"M[{Context.available_memory.pop()}]"

    except IndexError:
        raise ParserException(
            line_num,
            cur_line,
            f"No memory address available to assign to variable {name}.",
        )


def parse_C_instruction(line: str) -> CInstruction:
    # dest = rest
    if ":=" in line:
        dest, rest = line.split(":=")

    else:
        dest, rest = None, line

    # operation ; jmp
    if ";" in rest:
        rest = rest.replace(";IF", ";")
        operation_str, jmp = rest.split(";")

    else:
        jmp = None
        operation_str = rest

    # operand operation operand
    if "&" in operation_str:
        operation = Operations.AND

    elif "|" in operation_str:
        operation = Operations.OR if operation_str.count("|") == 1 else Operations.ABS

    elif "~" in operation_str:
        operation = Operations.NOT

    elif "+" in operation_str:
        operation = Operations.ADD

    elif "-" in operation_str:
        parts = filter_all(operation_str.split("-"))
        operation = Operations.SUB if len(parts) == 2 else Operations.NEG

    elif "*" in operation_str:
        operation = Operations.MULT

    elif "/" in operation_str and "_/" not in operation_str:
        operation = Operations.DIV

    elif "%" in operation_str:
        operation = Operations.MOD

    elif "_/" in operation_str:
        operation = Operations.SQRT

    elif "^" in operation_str:
        operation = Operations.XOR

    else:
        operation = Operations.NOP

    try:
        operands = filter_all(operation_str.split(operation.symbol))
    # empty separator (NOP)
    except ValueError:
        operands = [operation_str]

    if len(operands) != operation.multiplicity.value:
        raise ParserException(
            line_num,
            cur_line,
            f"Operation multiplicity ({operation.multiplicity.value}) and operand count ({len(operands)}) do not match.",
        )

    else:
        x, y = parse_operand(operands[0]), (
            parse_operand(operands[1]) if len(operands) != 1 else None
        )

    if dest is not None:
        dest = {parse_operand(d) for d in filter_all(dest.split(","))}

    if jmp is not None:
        has_dest: bool = not jmp.endswith("JMP")
        jmp = filter_all(jmp.split("JMP"))
        if len(jmp) > 2:
            raise ParserException(
                line_num,
                line,
                'The substring "JMP" is reserved within the jump part of a C instruction.',
            )

        match len(jmp):
            # compatibility case (already parsed and always jump)
            case 0:
                jmp = JumpType(Conditions.TRUE, constant_operand("0"), None)

            # has only destination, or comparison
            case 1:
                jmp = jmp[0]
                if has_dest:
                    jmp = JumpType(
                        Conditions.TRUE,
                        constant_operand("0"),
                        (jmp if jmp not in Context.symbols else Context.symbols[jmp]),
                    )

                else:
                    if "==" in jmp:
                        condition = Conditions.EQ

                    elif "!=" in jmp:
                        condition = Conditions.NE

                    elif "<=" in jmp:
                        condition = Conditions.LE

                    elif ">=" in jmp:
                        condition = Conditions.GE

                    elif "<" in jmp:
                        condition = Conditions.LT

                    elif ">" in jmp:
                        condition = Conditions.GT

                    else:
                        condition = Conditions.TRUE

                    jmp = filter_all(jmp.split(condition.value))[0]

                    jmp = JumpType(
                        condition,
                        parse_operand(jmp),
                        None,
                    )

            # has both condition and destination
            case 2:
                jmp_dest = (
                    jmp[1] if jmp[1] not in Context.symbols else Context.symbols[jmp[1]]
                )

                jmp = jmp[0]
                if "==" in jmp:
                    condition = Conditions.EQ

                elif "!=" in jmp:
                    condition = Conditions.NE

                elif "<=" in jmp:
                    condition = Conditions.LE

                elif ">=" in jmp:
                    condition = Conditions.GE

                elif "<" in jmp:
                    condition = Conditions.LT

                elif ">" in jmp:
                    condition = Conditions.GT

                else:
                    condition = Conditions.TRUE

                jmp = filter_all(jmp.split(condition.value))[0]

                jmp = JumpType(
                    condition,
                    parse_operand(jmp),
                    jmp_dest,
                )

    return CInstruction(line_num, x, y, operation, dest, jmp)


def parse_line(line: str) -> BaseInstruction | None:
    global line_num, cur_line

    ret_value: BaseInstruction | None = None
    line_num += 1
    cur_line = line

    if "@" in line:
        ret_value = parse_A_instruction(line)

    elif ":" in line and ":=" not in line:
        parse_alias(line)

    elif line.startswith("("):
        ret_value = parse_jump_label(line)

    elif line.startswith("VAR"):
        parse_variable(line)

    else:
        ret_value = parse_C_instruction(line)

    return ret_value


def parse_lines(
    file: list[str],
) -> list[BaseInstruction] | list[AInstruction | CInstruction]:
    instructions: list[BaseInstruction] = []
    for line in file:
        try:
            if (inst := parse_line(line)) is not None:
                instructions.append(inst)

        except ParserException as e:
            Context.exceptions.append(e)
            continue

    return instructions
