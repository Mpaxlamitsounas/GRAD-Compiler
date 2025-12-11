import Constants

# {M0, M1, M2, M3, M4, D, MM0, MM1, MM2, MM3} := {M0, M1, M2, M3, M4, A0, A1, A2, A3, A4, D, 1, MM0, MM1, MM2, MM3} + {M0, M1, M2, M3, M4, A0, A1, A2, A3, A4, D, 2, -, MM0, MM1, MM2, MM3}; IF >= {M0, M1, M2, M3, M4, A0, A1, A2, A3, A4, D, 1, -, MM0, MM1, MM2, MM3} JMP {A0, A1, A2, A3, A4}
# Same categories: Test Combinations
# Handcrafted tests for D and 1
# For y test with -
# Final test: Combination categories, combinations for same values, excluding for all same category


def run_test():
    Constants.run_test_cases()


if __name__ == "__main__":
    run_test()
