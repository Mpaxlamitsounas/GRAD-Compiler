#!./bin/python3
from pathlib import Path
from sys import argv

import Assembler
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

    # preprocess
    file = Preprocessor.process(file)

    # parse + assemble
    instructions: list[BaseInstruction] = []
    for inst in Parser.parse_instructions(file):
        print(str(inst))
        # instructions.extend(Assembler.decompress_instruction(inst))
    # with open(file_path.stem + ".a", "w") as f:
    #     f.writelines([str(inst) for inst in instructions])

    # compile
    # compile(file)
    # write to file


if __name__ == "__main__":
    argv.append("./fibonacci.txt")
    main()
