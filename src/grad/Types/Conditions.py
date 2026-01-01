from grad.Types import ConditionType

FALSE = ConditionType("", 0)
GT = ConditionType(">", 1)
EQ = ConditionType("==", 2)
GE = ConditionType(">=", 3)
LT = ConditionType("<", 4)
NE = ConditionType("!=", 5)
LE = ConditionType("<=", 6)
TRUE = ConditionType("", 7)


def get_from_value(condition: str) -> ConditionType:
    match condition:
        case ">":
            return GT

        case "==":
            return EQ

        case ">=":
            return GE

        case "<":
            return LT

        case "!=":
            return NE

        case "<=":
            return LE

        case _:
            return FALSE
