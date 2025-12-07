#!./bin/python3
from sys import argv

from Assembler import decompress
from Registers import A, M, D
from Types import CInstruction, Condition, JumpType, Operation

symbols: dict[str, str] = {}
reserved: tuple[str, ...] = ("@", "A", "M", "D", "=", ":", ";IF", "JMP", "+")


def remove_comments(file: list[str]):
    for line_idx, line in enumerate(file):
        if "//" in line:
            idx = line.find("//")
            file[line_idx] = line[0:idx]


def read_aliases(file: list[str]):
    for line in file:
        if ":" in line:
            key, value = (field.strip() for field in line.split(":"))
            if key in reserved:
                print(f'Alias name "{key}" is reserved.')
                raise KeyError
            symbols[key] = value


def remove_whitespace(file: list[str]):
    for line in file:
        line.replace(" ", "")

    try:
        while True:
            file.remove("")
    except ValueError:
        return

def main():
    if len(argv) != 2:
        print("Usage: compiler.py <filename>")
        return

    with open(argv[1], "rt", encoding="utf-8") as f:
        file = f.read().split("\n")

    # preprocess
    remove_comments(file)
    # read_aliases(file)
    # replace_aliases(file)
    remove_whitespace(file)

    # assemble
    print(*decompress(CInstruction(1, D(), D(), Operation.ADD, {D()}, JumpType(Condition.GE, A("4"), "5"))), sep="\n")
    # write to file

    # compile
    # compile(file)
    # write to file

    print(file)

if __name__ == "__main__":
    argv.append("./fibonacci.txt")
    main()
