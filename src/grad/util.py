from grad.Types import Operand, OperandType


def strip_all(s_list: list[str]) -> list[str]:
    return [s.strip() for s in s_list]


def strip_and_filter_all(s_list: list[str], exclude_str: str = "") -> list[str]:
    return [s for s in strip_all(s_list) if s.strip() != exclude_str]


ONE_register = Operand(OperandType.Register, "1")
TWO_register = Operand(OperandType.Register, "2")
D_register = Operand(OperandType.Register, "D")
A_register = Operand(OperandType.Register, "A")
M_simple_register = Operand(OperandType.Register, "M")


def is_M_register(op: Operand | None) -> bool:
    return op.value == "M" if op is not None else False


def constant_operand(value: str) -> Operand:
    if value == "1":
        return ONE_register

    if value == "2":
        return TWO_register

    return Operand(OperandType.Constant, value)


def is_valid_identifier_name(identifier: str) -> bool:
    if identifier == "":
        return False

    is_valid = all([c.isalnum() or c == "_" for c in identifier])
    if not is_valid:
        is_valid = is_valid_identifier_name(identifier[2:-1])

    return is_valid
