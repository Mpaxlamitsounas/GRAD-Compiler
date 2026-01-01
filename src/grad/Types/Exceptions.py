class GradException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class ParserException(GradException):
    pass


class AssemblerException(GradException):
    pass


class CompilerException(GradException):
    pass
