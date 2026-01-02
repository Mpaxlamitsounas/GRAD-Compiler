import random
from pathlib import Path

file_path = Path.cwd() / ".." / "Test" / "Test files" / "program.txt"

with open(file_path, "rt", encoding="utf-8") as f:
    s = f.read()

s_old = ""
while s != s_old:
    s_old = s
    s = s.replace("$REPLACE", str(random.randint(0, 100)), 1)

with open(file_path, "wt", encoding="utf-8") as f:
    f.write(s)
