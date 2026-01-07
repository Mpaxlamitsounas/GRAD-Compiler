import random
from pathlib import Path

dir_path = Path.cwd() / "Test" / "Compiler test files"

with open(dir_path / "selection_sort.template", "rt", encoding="utf-8") as f:
    s = f.read()

s_old = ""
while s != s_old:
    s_old = s
    s = s.replace("$REPLACE", str(random.randint(0, 100)), 1)

with open(dir_path / "selection_sort.grad", "wt", encoding="utf-8") as f:
    f.write(s)
