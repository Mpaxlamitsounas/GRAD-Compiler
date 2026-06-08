from typing import Literal

shuffle_variable_memory_pool: bool = True
use_only_dev_out_memory: bool = False # incompatible with shuffle_variable_memory_pool
apply_assembler_pattern_optimisations: bool = True
output_instruction_endianness: Literal["big", "little"] = "big"
output_intermediate_steps: bool = True
