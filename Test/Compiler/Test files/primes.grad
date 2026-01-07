VAR NUM
VAR CUR_DIVISOR
VAR BOUND

NUM := 2
(START_NUM_LOOP)
    BOUND := _/NUM

    // Prime check startup
    // Even check
    2; IF > BOUND JMP IS_PRIME
    NUM % 2; IF == 0 JMP IS_NOT_PRIME

    // Checks if divisible with odd numbers starting from 3
    CUR_DIVISOR := 1 + 2
    (START_PRIME_CHECK_LOOP)
        CUR_DIVISOR; IF > BOUND JMP IS_PRIME
        NUM % CUR_DIVISOR; IF == 0 JMP IS_NOT_PRIME
        CUR_DIVISOR := CUR_DIVISOR + 2
        1; JMP START_PRIME_CHECK_LOOP

    (IS_PRIME)
    DEV_OUT_0 := NUM

    (IS_NOT_PRIME)

    NUM := NUM + 1
    1; JMP START_NUM_LOOP
