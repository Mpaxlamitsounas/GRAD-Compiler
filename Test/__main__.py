from pathlib import Path

import Constants
import Handmade
import Memory_direct
import Memory_indirect
import Mixed
import Sequences


def run_tests():
    Constants.run_test_cases()
    Memory_direct.run_test_cases()
    Memory_indirect.run_test_cases()
    Mixed.run_test_cases()
    Handmade.run_test_cases()
    Sequences.run_test_cases()


if __name__ == "__main__":
    (Path.cwd() / "Output").mkdir(exist_ok=True)
    run_tests()
