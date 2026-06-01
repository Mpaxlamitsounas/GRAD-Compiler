#!./bin/python3
import random
import sys
from pathlib import Path
from sys import argv
from types import FrameType, TracebackType

from grad_compiler import Assembler, Compiler, Context, Options, Parser, Preprocessor
from grad_compiler.Context import default_symbols
from grad_compiler.Types.Exceptions import (
    AssemblerException,
    GradException,
    ParserException,
)
from grad_compiler.Types.Instructions import AInstruction, CInstruction


def initialise():
    random.seed("E20075")
    (Path.cwd() / "Output").mkdir(exist_ok=True)
    sys.argv[1] = sys.argv[1].upper()


def reset():
    Assembler.cur_A = None
    Parser.line_num = 0
    Parser.cur_line = ""
    Context.symbols = default_symbols.copy()
    Context.exceptions = []

    if Options.use_only_dev_out_memory:
        Context.available_memory = list(range(16388, 16400))

    if Options.shuffle_variable_memory_pool:
        random.shuffle(Context.available_memory)


def get_last_frame(traceback: TracebackType) -> FrameType:
    frame = traceback
    while frame.tb_next is not None:
        frame = frame.tb_next

    return frame.tb_frame


def format_exception(e: GradException) -> str:
    frame = get_last_frame(e.__traceback__)

    exception_path: str = frame.f_code.co_filename
    try:
        exception_path = str(Path(exception_path).relative_to(Path.cwd()))

    except ValueError:
        pass

    verb = (
        "parsing"
        if type(e) is ParserException
        else "assembling" if type(e) is AssemblerException else "compiling"
    )

    return f"""Encountered an error on line {e.line_num} while {verb}.
    Line content: {e.line}
    Error message: {e.message}
    Occurred in \"{exception_path}\" on line {frame.f_lineno} within \"{frame.f_code.co_name}\"
"""


def process_file(file: str):
    print(f"{"-" * 80}\nProcessing file {file}.")

    # preprocess
    file_path: Path = Path(file)
    with open(file_path, "rt", encoding="utf-8") as file:
        lines = Preprocessor.process_lines(file.read())

    # parse
    with open(
        Path.cwd() / "Output" / (file_path.stem + ".p"), "wt", encoding="utf-8"
    ) as file:
        parsed_instructions = Parser.parse_lines(lines)
        if Options.output_intermediate_steps:
            file.writelines([f"{inst}\n" for inst in parsed_instructions])

    # assemble
    assembled_instructions: list[AInstruction | CInstruction] | None = None
    if "A" in argv[1]:
        with open(
            Path.cwd() / "Output" / (file_path.stem + ".a"), "wt", encoding="utf-8"
        ) as file:
            assembled_instructions = Assembler.assemble_instructions(
                parsed_instructions
            )
            if Options.output_intermediate_steps:
                file.writelines([f"{inst}\n" for inst in assembled_instructions])

    # compile
    if "C" in argv[1] and len(Context.exceptions) == 0:
        if assembled_instructions is None:
            assembled_instructions = parsed_instructions

        with open(Path.cwd() / "Output" / (file_path.stem + ".c"), "wb") as file:
            compiled_instructions = Compiler.compile_instructions(
                assembled_instructions
            )
            if len(Context.exceptions) == 0:
                file.writelines(compiled_instructions)

    for exception in Context.exceptions:
        print(format_exception(exception))


def main():
    if len(argv) < 3 or (len(argv) > 1 and "H" in argv[1].upper()):
        print(f"""Usage: python -m grad <functions> <filename> [<filename>...]
Functions:
    {"a (Assemble)":12} - Assembles specified file
    {"c (Compile)":12} - Compiles Assemble output or specified file, instructions must be in Simple form
    {"h (Help)":12} - Displays this menu""")
        return

    initialise()

    for file in argv[2:]:
        reset()

        try:
            process_file(file)

        except KeyboardInterrupt:
            print("Received interrupt, exiting.")
            break

        except FileNotFoundError:
            print(f'Could not find file "{file}", continuing to next file.')

        except Exception as e:
            frame = get_last_frame(e.__traceback__)
            exception_path: str = frame.f_code.co_filename
            try:
                exception_path = str(Path(exception_path).relative_to(Path.cwd()))

            except ValueError:
                pass

            print(
                f"""Encountered unhandled exception, continuing to next file.
    Occurred in \"{exception_path}\" on line {frame.f_lineno} within \"{frame.f_code.co_name}\" and is of type \"{str(type(e))[8:-2]}\"\n"""
            )


if __name__ == "__main__":
    main()
