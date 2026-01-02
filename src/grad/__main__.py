#!./bin/python3
import random
import sys
from pathlib import Path
from sys import argv
from types import TracebackType, FrameType

from grad import Assembler, Compiler, Context, Parser, Preprocessor
from grad.Types.Exceptions import AssemblerException, CompilerException, ParserException
from grad.Types.Instructions import AInstruction, CInstruction


def process_file():
    # preprocess
    file_path: Path = Path(argv[2])
    with open(file_path, "rt", encoding="utf-8") as f:
        lines = Preprocessor.process_lines(f.read())

    # parse
    with open(
        Path.cwd() / "Output" / (file_path.stem + ".p"), "wt", encoding="utf-8"
    ) as f:
        parsed_instructions = Parser.parse_lines(lines, output_file=f)

    # assemble
    assembled_instructions: list[AInstruction | CInstruction] | None = None
    if "A" in argv[1]:
        with open(
            Path.cwd() / "Output" / (file_path.stem + ".a"), "wt", encoding="utf-8"
        ) as f:
            assembled_instructions = Assembler.assemble_instructions(
                parsed_instructions, output_file=f
            )

    # compile
    if "C" in argv[1]:
        if assembled_instructions is None:
            assembled_instructions = parsed_instructions

        with open(Path.cwd() / "Output" / (file_path.stem + ".c"), "wb") as f:
            Compiler.compile_instructions(assembled_instructions, output_file=f)


def get_last_frame(traceback: TracebackType) -> FrameType:
    frame = traceback
    while frame.tb_next is not None:
        frame = frame.tb_next
    return frame.tb_frame


def main():
    if len(argv) != 3:
        print(
            f"""Usage: python compiler.py <functions> <filename>
Functions:
    {"a (Assemble)":12} - Assembles specified file
    {"c (Compile)":12} - Compiles Assemble output or specified file, instructions must be in Simple form"""
        )
        return

    # initialise
    random.seed("E20075")
    random.shuffle(Context.available_RAM)
    (Path.cwd() / "Output").mkdir(exist_ok=True)
    sys.argv[1] = sys.argv[1].upper()

    try:
        process_file()

    except ParserException as e:
        frame = get_last_frame(e.__traceback__)

        print(
            f"""Encountered an error while parsing line {e.line_num}
    Line content: {e.line}
    Error message: {e.message}
    Occurred in \"{frame.f_code.co_filename}\" on line {frame.f_lineno} within \"{frame.f_code.co_name}\"
"""
        )
        return

    except AssemblerException as e:
        frame = get_last_frame(e.__traceback__)

        print(
            f"""Encountered an error while assembling line {e.line_num}
    Line content: {e.line}
    Error message: {e.message}
    Occurred in \"{frame.f_code.co_filename}\" on line {frame.f_lineno} within \"{frame.f_code.co_name}\""""
        )
        return

    except CompilerException as e:
        frame = get_last_frame(e.__traceback__)

        print(
            f"""Encountered an error while compiling line {e.line_num}
    Line content: {e.line}
    Error message: {e.message}
    Occurred in \"{frame.f_code.co_filename}\" on line {frame.f_lineno} within \"{frame.f_code.co_name}\""""
        )
        return


if __name__ == "__main__":
    main()
