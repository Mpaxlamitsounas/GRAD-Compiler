from pathlib import Path

from GRAD_machine.util import (
    BIT_PATTERN_ALTERNATING_1,
    BIT_PATTERN_ALTERNATING_2,
    GRAD_INT_MAX,
    GRAD_INT_MIN,
    to_binary,
)

from Test.GRAD_machine.Types import ALUCase, ALUFlags


def make_test_cases(cases: list[ALUCase], file_name: str):
    cases_str: list[str] = [
        "x                  y                  out                zx nx zy ny f    no zr ng\n"
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
    make_test_cases(
        [
            ALUCase(0, 0, 0, ALUFlags.AND),
            ALUCase(0, 0, GRAD_INT_MIN, ALUFlags.no),
            ALUCase(1, 1, 0, ALUFlags.zx),
            ALUCase(1, 1, 0, ALUFlags.zy),
            ALUCase(1, 1, ~1, ALUFlags.nx | ALUFlags.ny),
            ALUCase(~1, ~1, 1, ALUFlags.no),
        ],
        "flags.t",
    )

    # Test AND
    make_test_cases(
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
    make_test_cases(
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
                GRAD_INT_MIN,
                ALUFlags.OR,
            ),
        ],
        "OR.t",
    )


if __name__ == "__main__":
    main()
