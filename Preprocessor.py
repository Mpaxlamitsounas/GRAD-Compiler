from Context import reserved, symbols


def remove_comments(line: str) -> str:
    if "//" in line:
        idx = line.find("//")
        return line[0:idx]
    else:
        return line


def read_aliases(file: list[str]):
    for line in file:
        if ":" in line:
            key, value = (field.strip() for field in line.split(":"))
            if key in reserved:
                print(f'Alias name "{key}" is reserved.')
                raise KeyError
            symbols[key] = value


def remove_sugar(line: str) -> str:
    return line.replace("IF", "")


def remove_whitespace(line: str) -> str | None:
    line = line.strip()
    return line if line != "" else None


def process(file: list[str]) -> list[str]:
    lines: list[str] = []
    for line in file:
        line = line.upper()
        line = remove_comments(line)
        # read_aliases(file)
        # replace_aliases(file)
        line = remove_sugar(line)
        line = remove_whitespace(line)
        if line is not None:
            lines.append(line)

    return lines
