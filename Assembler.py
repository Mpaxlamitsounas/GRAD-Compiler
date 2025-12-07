from Parser import parse_operand

# Memory loading: Reg -> C, Con -> A
# (Reg, Reg)
# M[1] => A = 1; M
# M[D] => A = D; M
# M[M[1]] => A = 1; A = M; M
#
# (Reg, Con)
# M[3] => @3; M
# M[M[3]] => @3; A = M; M
#
#
# Calc: Reg -> No load, Con -> A
# (Reg, Con)
# y + 1 => y + 1
# (Reg, Con)
# y + D => y + D
# (Con, Con)
# y + 3 => @3; y + A


# # TODO
# def _decompress_A_instruction(inst: AInstruction) -> list[Instruction]:
#     return[inst]
#
# def _check_instruction_validity(inst: CInstruction) -> bool:
#     if inst.dest is None and inst.jmp is None:
#         print(f"INFO Skipping instruction with no effect {inst}")
#         return False
#
#     elif Register.ONE in inst.dest or Register.TWO in inst.dest:
#         print(f"ERROR Can only assign to registers A, M, or D.")
#         return False
#
#     elif len([dest for dest in inst.dest if dest.register == Register.M]) > 1:
#         print(f"ERROR Can output to at most one memory location at a time.")
#         return False
#
#     elif inst.op == Operation.NOP and inst.y is not None:
#         print("ERROR Unary operations accept only one operand.")
#         return False
#
#     return True
#
# def _decompress_operation_part(cur_A: str | None, inst: CInstruction, instructions: list[Instruction]) -> str | None:
#     if inst.x.register == Register.M:
#         if inst.y is not None and inst.y.register == Register.M:
#             if inst.x.address != inst.y.address:
#                 instructions.extend(
#                     [
#                         AInstruction(inst.line_num, inst.x.address),
#                         CInstruction(inst.line_num, inst.x, None, Operation.NOP, {D()}),
#                         AInstruction(inst.line_num, inst.y.address),
#                         CInstruction(
#                             inst.line_num, D(), inst.y, inst.op, inst.dest, inst.jmp
#                         ),
#                     ]
#                 )
#
#                 cur_A = inst.y.address
#             else:
#                 instructions.extend(
#                     [
#                         AInstruction(inst.line_num, inst.x.address),
#                         CInstruction(
#                             inst.line_num, inst.x, inst.y, inst.op, inst.dest, inst.jmp
#                         ),
#                     ]
#                 )
#
#                 cur_A = inst.x.address
#
#         elif inst.x.register == Register.M:
#             instructions.extend(
#                 [
#                     AInstruction(inst.line_num, inst.x.address),
#                     CInstruction(
#                         inst.line_num, inst.x, inst.y, inst.op, inst.dest, inst.jmp
#                     ),
#                 ]
#             )
#
#             cur_A = inst.x.address
#
#     elif inst.y is not None and inst.y.register == Register.M:
#         instructions.extend(
#             [
#                 AInstruction(inst.line_num, inst.y.address),
#                 CInstruction(
#                     inst.line_num, inst.x, inst.y, inst.op, inst.dest, inst.jmp
#                 ),
#             ]
#         )
#
#         cur_A = inst.y.address
#
#     else:
#         instructions.append(inst)
#
#     return cur_A
#
# def _decompress_destination_part(cur_A: str | None, inst: CInstruction, instructions: list[Instruction]) -> str | None:
#     if len(inst.dest) > 0 and any([d.register == Register.M for d in inst.dest]):
#         address: str = [d.address for d in inst.dest if d.register == Register.M][0]
#         if cur_A is None:
#             instructions.insert(0, AInstruction(inst.line_num, address))
#             cur_A = address
#
#         elif address != cur_A:
#             prev_inst: CInstruction = instructions[-1]
#             del instructions[-1]
#             instructions.extend(
#                 [
#                     CInstruction(
#                         inst.line_num,
#                         prev_inst.x,
#                         prev_inst.y,
#                         prev_inst.op,
#                         {D()},
#                         None,
#                     ),
#                     AInstruction(inst.line_num, address),
#                     CInstruction(
#                         inst.line_num,
#                         D(),
#                         None,
#                         Operation.NOP,
#                         prev_inst.dest,
#                         prev_inst.jmp,
#                     ),
#                 ]
#             )
#
#             cur_A = address
#
#     return cur_A
#
#
# def _decompress_jmp_condition_part(cur_A: str | None, inst: CInstruction,
#                                    instructions: list[Instruction]) -> str | None:
#     if inst.jmp.compared.address != "0":
#         prev_inst: CInstruction = instructions[-1]
#         prev_inst.dest.add(D())
#         del instructions[-1]
#
#         if inst.jmp.compared.register == Register.A:
#             sub_reg = A(None)
#         else:
#             sub_reg = M(inst.jmp.compared.address)
#
#         instructions.extend(
#             [
#                 CInstruction(
#                     inst.line_num,
#                     prev_inst.x,
#                     prev_inst.y,
#                     prev_inst.op,
#                     prev_inst.dest,
#                 ),
#                 CInstruction(
#                     inst.line_num,
#                     D(),
#                     sub_reg,
#                     Operation.SUB,
#                     set(),
#                     JumpType(
#                         prev_inst.jmp.condition,
#                         RegisterType(Register.A, "0"),
#                         prev_inst.jmp.destination,
#                     ),
#                 ),
#             ]
#         )
#
#         if cur_A is None or cur_A != inst.jmp.compared.address:
#             instructions.insert(
#                 -1, AInstruction(inst.line_num, inst.jmp.compared.address)
#             )
#
#         cur_A = inst.jmp.compared.address
#
#     return cur_A
#
# def _decompress_jmp_destination_part(cur_A: str | None, inst: CInstruction,
#                                      instructions: list[Instruction]):
#     prev_inst: CInstruction = instructions[-1]
#     prev_jmp = prev_inst.jmp
#
#     if cur_A is None:
#         instructions.insert(
#             -1, AInstruction(inst.line_num, prev_jmp.destination)
#         )
#
#     elif inst.jmp.destination != cur_A:
#         prev_inst.dest.add(D())
#         prev_inst.jmp = None
#
#         instructions.extend([AInstruction(inst.line_num, prev_jmp.destination),
#                              CInstruction(inst.line_num, D(), None, Operation.NOP, set(), prev_jmp)]
#                             )
#
# def _decompress_C_instruction(inst: CInstruction):
#
#     is_valid = _check_instruction_validity(inst)
#     if not is_valid:
#         return []
#
#
#     instructions: list[Instruction] = []
#     cur_A: str | None = None
#     params: tuple[CInstruction, list[Instruction]] = (inst, instructions)
#
#     cur_A = _decompress_operation_part(cur_A, *params)
#     cur_A = _decompress_destination_part(cur_A, *params)
#     if inst.jmp is not None:
#         cur_A = _decompress_jmp_condition_part(cur_A, *params)
#         _decompress_jmp_destination_part(cur_A, *params)
#
#     return instructions
#
#
# def decompress_instruction(inst: Instruction) -> list[Instruction]:
#     match inst.inst_type:
#         case InstructionType.A:
#             return _decompress_A_instruction(inst)
#         case InstructionType.C:
#             return _decompress_C_instruction(inst)
