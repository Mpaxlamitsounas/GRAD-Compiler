from dataclasses import dataclass


@dataclass
class GradException(Exception):
    line_num: int
    line: str
    message: str


class ParserException(GradException):
    pass


class AssemblerException(GradException):
    pass


class CompilerException(GradException):
    pass
