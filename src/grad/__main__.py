#!./bin/python3
import random
import sys
from pathlib import Path
from sys import argv
from types import FrameType, TracebackType

from grad import Assembler, Compiler, Context, Options, Parser, Preprocessor
from grad.Context import default_symbols
from grad.Types.Exceptions import (
    AssemblerException,
    CompilerException,
    GradException,
    ParserException,
)
from grad.Types.Instructions import AInstruction, CInstruction


def initialise():
    random.seed("E20075")
    (Path.cwd() / "Output").mkdir(exist_ok=True)
    sys.argv[1] = sys.argv[1].upper()


def reset():
    Assembler.cur_A = None
    Parser.line_num = 0
    Parser.cur_line = ""
    Context.symbols = default_symbols.copy()

    if Options.use_dev_out_memory:
        Context.available_memory = list(range(16388, 16400))

    if Options.shuffle_memory:
        random.shuffle(Context.available_memory)


def process_file(file: str):
    # preprocess
    file_path: Path = Path(file)
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


def format_exception(verb: str, file: str, e: GradException) -> str:
    frame = get_last_frame(e.__traceback__)

    return f"""Encountered an error on line {e.line_num} while {verb} file \"{file}\", continuing to next file.
    Line content: {e.line}
    Error message: {e.message}
    Occurred in \"{frame.f_code.co_filename}\" on line {frame.f_lineno} within \"{frame.f_code.co_name}\"
"""


def main():
    if len(argv) < 3 or (len(argv) > 1 and "H" in argv[1].upper()):
        print(
            f"""Usage: python -m grad <functions> <filename> [<filename>...]
Functions:
    {"a (Assemble)":12} - Assembles specified file
    {"c (Compile)":12} - Compiles Assemble output or specified file, instructions must be in Simple form"""
        )
        return

    initialise()

    for file in argv[2:]:
        reset()

        try:
            process_file(file)

        except ParserException as e:
            print(format_exception("parsing", file, e))

        except AssemblerException as e:
            print(format_exception("assembling", file, e))

        except CompilerException as e:
            print(format_exception("compiling", file, e))

        except KeyboardInterrupt:
            print("Received interrupt, exiting.")
            break

        except FileNotFoundError:
            print(f'Could not find file "{file}", continuing to next file.')

        except Exception as e:
            frame = get_last_frame(e.__traceback__)

            print(
                f"""Caught unhandled exception while processing file \"{file}\", continuing to next file.
    Occurred in \"{frame.f_code.co_filename}\" on line {frame.f_lineno} within \"{frame.f_code.co_name}\" and is of type \"{str(type(e))[8:-2]}\""""
            )


if __name__ == "__main__":
    main()
