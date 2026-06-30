import random
import sys
from pathlib import Path

from grad_compiler import Assembler, Context, Options, Parser
from grad_compiler.Types import SymbolStore


def reset():
    Assembler.cur_A = None
    Parser.line_num = 0
    Parser.cur_line = ""
    Context.symbols = SymbolStore(Context.default_symbols)
    Context.available_memory = Context.default_available_memory.copy()
    Context.exceptions = []
    random.seed("E20075")

    if Options.shuffle_variable_memory_pool:
        random.shuffle(Context.available_memory)

    if Options.use_only_dev_out_memory:
        Context.available_memory = list(range(16388, 16400))


def initialise():
    (Path.cwd() / "Output").mkdir(exist_ok=True)
    if len(sys.argv) > 1:
        sys.argv[1] = sys.argv[1].upper()
    reset()
