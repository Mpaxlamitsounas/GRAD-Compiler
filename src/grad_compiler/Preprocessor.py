def remove_comments(line: str) -> str:
    if "//" in line:
        idx = line.find("//")
        return line[0:idx]

    else:
        return line


def process_lines(file: str) -> list[str]:
    lines: list[str] = []
    for line in file.split("\n"):
        line = line.upper()
        line = remove_comments(line)
        line = line.replace(" ", "")
        if line != "":
            lines.append(line)

    return lines
