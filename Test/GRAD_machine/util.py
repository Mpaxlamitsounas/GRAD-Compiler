GRAD_INT_MAX = 2**15 - 1
GRAD_INT_MIN = 2**16 - 1
BIT_PATTERN_ALTERNATING_1 = 0b1010101010101010
BIT_PATTERN_ALTERNATING_2 = 0b0101010101010101


def to_binary(num: int) -> int:
    if num < 0:
        num = (-num ^ 0b1111111111111111) + 1

    return num
