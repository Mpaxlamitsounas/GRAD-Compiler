from grad.Types.Instructions import BaseInstruction


class GradException(Exception):
    def __init__(self, msg: str, inst: BaseInstruction):
        self.msg = msg
        self.inst = inst


class ParserException(GradException):
    pass


class AssemblerException(GradException):
    pass


class CompilerException(GradException):
    pass
