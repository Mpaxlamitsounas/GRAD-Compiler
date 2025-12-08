#!./bin/python3
import random
from pathlib import Path
from sys import argv

import Context
import Parser
import Preprocessor
from Types.Instructions import BaseInstruction


def main():
    if len(argv) != 2:
        print("Usage: compiler.py <filename>")
        return

    file_path: Path = Path(argv[1])
    with open(file_path, "rt", encoding="utf-8") as f:
        file = f.read().split("\n")

    # initialise
    random.seed = "E20075"
    random.shuffle(Context.available_RAM)

    # preprocess
    file = Preprocessor.process(file)

    # parse
    parsed_instructions: list[BaseInstruction] = Parser.parse_instructions(file)
    with open(file_path.stem + ".p", "w") as f:
        f.writelines([f"{inst}\n" for inst in parsed_instructions])

    # assemble
    # decompressed_instructions: list[BaseInstruction] = Assembler.decompress_instructions(parsed_instructions)
    # with open(file_path.stem + ".a", "w") as f:
    #     f.writelines([str(inst) for inst in decompressed_instructions])

    # compile
    # compile(file)
    # write to file


if __name__ == "__main__":
    argv.append("./fibonacci.txt")
    main()
