from Types import Operand, OperandType


def strip_all(s_list: list[str]) -> list[str]:
    return [s.strip() for s in s_list]


def strip_and_filter_all(s_list: list[str], exclude_str: str = "") -> list[str]:
    return [s for s in strip_all(s_list) if s.strip() != exclude_str]


def D_register() -> Operand:
    return Operand(OperandType.Register, "D")


def A_register() -> Operand:
    return Operand(OperandType.Register, "A")


def M_register(operand: Operand | None) -> Operand:
    return Operand(OperandType.Register, "M", operand)


def constant_operand(value: str) -> Operand:
    return Operand(OperandType.Constant, value)
