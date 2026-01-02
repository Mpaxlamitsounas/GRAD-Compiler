default_symbols: dict[str, str] = (
    {f"M{idx}": f"M[{idx}]" for idx in range(0, 64)}
    | {f"DEV_IN_{idx}": f"M[{idx + 2**14}]" for idx in range(4)}
    | {f"DEV_OUT_{idx}": f"M[{idx + 2**14 + 4}]" for idx in range(12)}
    | {"DEV_IN_START_ADD": str(2**14)}
    | {"DEV_OUT_START_ADD": str(2**14 + 4)}
)
symbols: dict[str, str] = default_symbols.copy()
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
available_memory: list[int] = list(range(2**14, 64, -1))
