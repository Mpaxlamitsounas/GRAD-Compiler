#!./bin/python3
import os
import random
from pathlib import Path
from sys import argv

from grad import Assembler, Context, Parser, Preprocessor


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
    parsed_instructions = Parser.parse_instructions(file)
    with open("Generated/" + file_path.stem + ".p", "wt") as f:
        f.writelines([f"{inst}\n" for inst in parsed_instructions])

    # assemble
    assembled_instructions = Assembler.run_full_pipeline(parsed_instructions)
    with open("Generated/" + file_path.stem + ".a", "wt") as f:
        f.writelines([f"{inst}\n" for inst in assembled_instructions])

    # compile
    # compile(file)
    # write to file


if __name__ == "__main__":
    if argv[1] == "all":
        for file in os.listdir("Test files"):
            argv[1] = "./Test files/" + file
            main()
    elif argv[1] == "test":
        argv[1] = "./Test files/" + "test.txt"
        main()
