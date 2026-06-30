from collections.abc import Callable
from pathlib import Path

from grad_compiler import Assembler, Parser, reset
from grad_compiler.Types import Operand
from grad_compiler.Types.Instructions import BaseInstruction


def make_combination_cases(length: int) -> list[tuple[bool, ...]]:
    perms: list[tuple[bool, ...]] = [tuple([False] * (length - 1))]
    for i in range(1, 2 ** (length - 1)):
        i_bin = "0" * (length - 1 - i.bit_length()) + bin(i)[2:]
        perms.append(tuple([True if d == "1" else False for d in i_bin]))

    return perms


def write_lines_to_file(filename: Path | str, lines: list[str]):
    with open(Path.cwd() / "Output" / filename, "w") as f:
        f.writelines([str(line) + "\n" for line in lines])


def get_inst_values(
    unique_values: list[str], case: tuple[bool, ...]
) -> tuple[Operand, ...]:
    values = [unique_values.pop(0)] * (len(case) + 1)
    for idx, different in enumerate(case):
        values[idx + 1] = unique_values.pop(0) if different else values[idx]

    return tuple([Parser.parse_operand(v) for v in values])


def run_test_case(value_set: list[str], inst_builder: Callable, filename: Path | str):
    cases = make_combination_cases(len(value_set))

    results: list[BaseInstruction | str] = []
    for case in cases:
        reset()
        values = get_inst_values(value_set.copy(), case)
        inst = inst_builder(values)
        results.extend([inst, "---", *Assembler.assemble_instructions([inst]), ""])

    write_lines_to_file(filename, results)


def run_test_case_sequence(instructions: list[BaseInstruction], filename: Path | str):
    results: list[BaseInstruction | str] = instructions
    results.append("---")
    results.extend(Assembler.assemble_instructions(instructions))
    results.append("")

    write_lines_to_file(filename, results)
