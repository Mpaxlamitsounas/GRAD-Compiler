symbols: dict[str, str] = {f"M{idx}": f"M[{idx}]" for idx in range(0, 64)}
# TODO
reserved: tuple[str, ...] = (
    "@",
    ":=",
    ":",
    ";",
    "IF",
    "JMP",
    "VAR",
    "+",
)
available_RAM: list[int] = list(range(64, 16384))
