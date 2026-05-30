from typing import TextIO


def remove_comments(line: str) -> str:
    if "//" in line:
        idx = line.find("//")
        return line[0:idx]
    else:
        return line


def process_lines(file: str, output_file: TextIO | None = None) -> list[str]:
    lines: list[str] = []
    for line in file.split("\n"):
        line = line.upper()
        line = remove_comments(line)
        line = line.strip()
        if line != "":
            lines.append(line)

            if output_file is not None:
                output_file.write(line)

    return lines
