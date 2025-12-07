import Context
from Types import Condition, JumpType, Operand, OperandType
from Types.Instructions import AInstruction, BaseInstruction, CInstruction
from Types.Operations import Multiplicity, Operation


def parse_operand(operand: str) -> Operand:
    if operand == "D":
        return Operand(OperandType.Register, "D")
    elif operand == "A":
        return Operand(OperandType.Register, "A")
    # M
    elif "[" in operand:
        operand = operand[2:-1]
        return Operand(OperandType.Register, "M", operand)
    elif operand in Context.symbols:
        return Operand(OperandType.Constant, value=Context.symbols[operand])
    else:
        return Operand(OperandType.Constant, value=operand)


def parse_instructions(file: list[str]) -> list[BaseInstruction]:
    instructions: list[BaseInstruction] = []
    line_num: int = 0

    for line in file:
        # A-Instruction
        if "@" in line:
            instructions.append(AInstruction(line_num, line.strip("@ ")))

        # Alias
        elif ":" in line and ":=" not in line:
            key, value = line.split(":")
            if key == "" or value == "":
                raise ValueError
            Context.symbols[key] = value

        # # Jump label
        # elif line.startswith("("):
        #     name = line[1:-2]
        #     if len(name) == 0:
        #         raise ValueError
        #
        #     Context.symbols[name] = line_num

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
            else:
                jmp = None
                operation_str = rest

            # operand operation operand
            if "+" in operation_str:
                operation = Operation.ADD
            else:
                operation = Operation.NOP

            try:
                operands = [oper.strip() for oper in operation_str.split(operation.symbol) if oper.strip() != ""]
            # empty separator (NOP)
            except ValueError:
                operands = [operation_str] if operation_str != "" else []

            if len(operands) != operation.multiplicity.value:
                raise ValueError

            else:
                x, y = parse_operand(operands[0]), (
                    parse_operand(operands[1]) if len(operands) != 1 else None
                )

            if dest is not None:
                dest = {parse_operand(d.strip()) for d in dest.split(",")}

            if jmp is not None:
                jmp = [j.strip() for j in jmp.split("JMP") if j.strip() != ""]
                if len(jmp) == 1:
                    jmp = JumpType(Condition.TRUE, None, jmp[0])

                elif len(jmp) == 2:
                    jmp_dest = jmp[1]
                    try:
                        jmp_cond, jmp_oper = [
                            j.strip() for j in jmp[0].split() if j.strip() != ""
                        ]
                    except:
                        raise ValueError

                    jmp = JumpType(
                        Condition(jmp_cond), parse_operand(jmp_oper), jmp_dest
                    )

                else:
                    raise ValueError

            instructions.append(CInstruction(line_num, x, y, operation, dest, jmp))

        line_num += 1

    return instructions
