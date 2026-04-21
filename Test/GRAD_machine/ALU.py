from pathlib import Path

from GRAD_machine.util import (
    BIT_PATTERN_ALTERNATING_1,
    BIT_PATTERN_ALTERNATING_2,
    GRAD_INT_MAX,
    GRAD_INT_MIN,
    to_binary,
)
from Test.GRAD_machine.Types import ALUCase, ALUFlags


def run_test_cases(cases: list[ALUCase], file_name: str):
    cases_str: list[str] = [
        "x                  y                  out                zx nx zy ny f      no zr ng\n"
    ]
    for case in cases:
        out = to_binary(case.out)
        cases_str.append(
            f"{format(to_binary(case.x), "#018b")} {format(to_binary(case.y), "#018b")} {format(out, "#018b")} {case.flags.to_ALU_input()}  {"1" if case.out == 0 else "0"}  {"1" if out > GRAD_INT_MAX else "0"}\n"
        )

    with open(Path.cwd() / "Test files" / file_name, "wt", encoding="utf-8") as f:
        f.writelines(cases_str)


def main():
    # Test flags
    run_test_cases(
        [
            ALUCase(0, 0, 0, ALUFlags.AND),
            ALUCase(0, 0, -1, ALUFlags.no),
            ALUCase(1, 1, 0, ALUFlags.zx),
            ALUCase(1, 1, 0, ALUFlags.zy),
            ALUCase(1, 1, ~1, ALUFlags.nx | ALUFlags.ny),
            ALUCase(~1, ~1, 1, ALUFlags.no),
        ],
        "flags.t",
    )

    # Test AND
    run_test_cases(
        [
            ALUCase(0, 0, 0, ALUFlags.AND),
            ALUCase(~0, ~0, ~0, ALUFlags.AND),
            ALUCase(~0, 0, 0, ALUFlags.AND),
            ALUCase(
                BIT_PATTERN_ALTERNATING_1, BIT_PATTERN_ALTERNATING_2, 0, ALUFlags.AND
            ),
            ALUCase(
                BIT_PATTERN_ALTERNATING_1,
                BIT_PATTERN_ALTERNATING_2,
                BIT_PATTERN_ALTERNATING_1,
                ALUFlags.AND | ALUFlags.ny,
            ),
        ],
        "AND.t",
    )

    # Test OR
    run_test_cases(
        [
            ALUCase(0, 0, 0, ALUFlags.OR),
            ALUCase(~0, 0, ~0, ALUFlags.OR),
            ALUCase(
                BIT_PATTERN_ALTERNATING_1, BIT_PATTERN_ALTERNATING_2, ~0, ALUFlags.OR
            ),
            ALUCase(
                BIT_PATTERN_ALTERNATING_1, 0, BIT_PATTERN_ALTERNATING_1, ALUFlags.OR
            ),
            ALUCase(
                BIT_PATTERN_ALTERNATING_1,
                0,
                BIT_PATTERN_ALTERNATING_2,
                ALUFlags.OR & ~ALUFlags.no,
            ),
            ALUCase(
                BIT_PATTERN_ALTERNATING_1,
                BIT_PATTERN_ALTERNATING_2,
                -1,
                ALUFlags.OR,
            ),
        ],
        "OR.t",
    )

    # Test NOT
    run_test_cases(
        [
            ALUCase(
                BIT_PATTERN_ALTERNATING_1, 0, BIT_PATTERN_ALTERNATING_2, ALUFlags.NOT
            ),
            ALUCase(
                BIT_PATTERN_ALTERNATING_1,
                0,
                BIT_PATTERN_ALTERNATING_1,
                ALUFlags.NOT | ALUFlags.no,
            ),
        ],
        "NOT.t",
    )

    # Test ADD
    run_test_cases(
        [
            ALUCase(1, 1, 1, ALUFlags.ADD | ALUFlags.zx),
            ALUCase(1, 1, 1, ALUFlags.ADD | ALUFlags.zy),
            ALUCase(1, 1, 2, ALUFlags.ADD),
            ALUCase(1, -1, 0, ALUFlags.ADD),
            ALUCase(-1, -1, -2, ALUFlags.ADD),
            ALUCase(GRAD_INT_MIN + GRAD_INT_MAX, 1, 0, ALUFlags.ADD),
            ALUCase(GRAD_INT_MAX, 1, 0b1000000000000000, ALUFlags.ADD),
            ALUCase(1, 1, -1, ALUFlags.ADD | ALUFlags.nx),
        ],
        "ADD.t",
    )

    # Test SUB
    run_test_cases(
        [
            ALUCase(1, 1, -1, ALUFlags.SUB | ALUFlags.zx),
            ALUCase(1, 1, 1, ALUFlags.SUB | ALUFlags.zy),
            ALUCase(1, 1, 0, ALUFlags.SUB),
            ALUCase(1, -1, 2, ALUFlags.SUB),
            ALUCase(-1, -1, 0, ALUFlags.SUB),
        ],
        "SUB.t",
    )

    # Test NEG
    run_test_cases(
        [
            ALUCase(1, 0, -1, ALUFlags.NEG),
            ALUCase(GRAD_INT_MAX, 0, -GRAD_INT_MAX, ALUFlags.NEG),
            ALUCase(GRAD_INT_MAX, 0, GRAD_INT_MAX + 2, ALUFlags.NEG),
        ],
        "NEG.t",
    )

    # Test MULT
    run_test_cases(
        [
            ALUCase(1, 0, 0, ALUFlags.MULT),
            ALUCase(1, 1, 0, ALUFlags.MULT | ALUFlags.zx),
            ALUCase(1, -1, -1, ALUFlags.MULT),
            ALUCase(1, -0, 0, ALUFlags.MULT),
            ALUCase(-1, 1, -1, ALUFlags.MULT),
            ALUCase(-1, -1, 1, ALUFlags.MULT),
            ALUCase(GRAD_INT_MAX, 2, 2 * GRAD_INT_MAX, ALUFlags.MULT),
        ],
        "MULT.t",
    )

    # Test DIV
    run_test_cases(
        [
            ALUCase(1, 1, 1, ALUFlags.DIV),
            ALUCase(1, 1, 0, ALUFlags.DIV | ALUFlags.zx),
            ALUCase(1, -1, -1, ALUFlags.DIV),
            ALUCase(0, -1, 0, ALUFlags.DIV),
            ALUCase(-1, 1, -1, ALUFlags.DIV),
            ALUCase(-1, -1, 1, ALUFlags.DIV),
            ALUCase(GRAD_INT_MAX, 2, GRAD_INT_MAX // 2, ALUFlags.DIV),
            ALUCase(1, 4, 0, ALUFlags.DIV),
            ALUCase(5, 4, 1, ALUFlags.DIV),
            ALUCase(-1, 4, -1 // 4, ALUFlags.DIV),
            ALUCase(-5, 4, -5 // 4, ALUFlags.DIV),
            ALUCase(1, -4, 1 // -4, ALUFlags.DIV),
            ALUCase(5, -4, 5 // -4, ALUFlags.DIV),
            ALUCase(-1, -4, -1 // -4, ALUFlags.DIV),
            ALUCase(-5, -4, -5 // -4, ALUFlags.DIV),
            ALUCase(1, 0, -1, ALUFlags.DIV),
            ALUCase(-1, 0, 0, ALUFlags.DIV),
        ],
        "DIV.t",
    )

    # Test MOD
    run_test_cases(
        [
            ALUCase(1, 4, 1, ALUFlags.MOD),
            ALUCase(5, 4, 1, ALUFlags.MOD),
            ALUCase(-1, 4, -1 % 4, ALUFlags.MOD),
            ALUCase(-5, 4, -5 % 4, ALUFlags.MOD),
            ALUCase(1, -4, 1 % -4, ALUFlags.MOD),
            ALUCase(5, -4, 5 % -4, ALUFlags.MOD),
            ALUCase(-1, -4, -1 % -4, ALUFlags.MOD),
            ALUCase(-5, -4, -5 % -4, ALUFlags.MOD),
            ALUCase(1, 0, 1, ALUFlags.MOD),
            ALUCase(-1, 0, -1, ALUFlags.MOD),
        ],
        "MOD.t",
    )

    # Test ABS
    run_test_cases(
        [
            ALUCase(1, 0, 1, ALUFlags.ABS),
            ALUCase(-1, 0, 1, ALUFlags.ABS),
            ALUCase(-GRAD_INT_MAX, 0, GRAD_INT_MAX, ALUFlags.ABS),
        ],
        "ABS.t",
    )

    # Test SQRT
    run_test_cases(
        [
            ALUCase(0, 0, 0, ALUFlags.SQRT),
            ALUCase(1, 0, 1, ALUFlags.SQRT),
            ALUCase(2, 0, 1, ALUFlags.SQRT),
            ALUCase(4, 0, 2, ALUFlags.SQRT),
            ALUCase(GRAD_INT_MAX, 0, 181, ALUFlags.SQRT),
            ALUCase(GRAD_INT_MIN + GRAD_INT_MAX, 0, 255, ALUFlags.SQRT),
            ALUCase(GRAD_INT_MIN, 0, 181, ALUFlags.SQRT),
        ],
        "SQRT.t",
    )

    # Test NOP
    run_test_cases(
        [
            ALUCase(0, 0, 0, ALUFlags.NOP),
            ALUCase(1, 0, 1, ALUFlags.NOP),
        ],
        "NOP.t",
    )

    # Test XOR
    run_test_cases(
        [
            ALUCase(0, 0, 0, ALUFlags.XOR),
            ALUCase(0b1111111111111111, 0, 0b1111111111111111, ALUFlags.XOR),
            ALUCase(0, 0b1111111111111111, 0b1111111111111111, ALUFlags.XOR),
            ALUCase(
                BIT_PATTERN_ALTERNATING_1,
                BIT_PATTERN_ALTERNATING_2,
                0b1111111111111111,
                ALUFlags.XOR,
            ),
            ALUCase(0b1111111111111111, 0b1111111111111111, 0, ALUFlags.XOR),
        ],
        "XOR.t",
    )


if __name__ == "__main__":
    main()
