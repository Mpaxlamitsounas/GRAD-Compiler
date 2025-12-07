from Types import Register, RegisterArg

A = lambda address: RegisterArg(Register.A, address)
M = lambda address: RegisterArg(Register.M, address)
D = lambda: RegisterArg(Register.D)
