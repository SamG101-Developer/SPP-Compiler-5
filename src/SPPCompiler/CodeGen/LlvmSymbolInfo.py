from dataclasses import dataclass
from typing import Optional

from llvmlite import ir


@dataclass(slots=True, repr=False, kw_only=True)
class LlvmTypeSymbolInfo:
    llvm_type: ir.IdentifiedStructType
    llvm_module: ir.Module


@dataclass(slots=True, repr=False, kw_only=True)
class LlvmVariableSymbolInfo:
    ptr: Optional[ir.AllocaInstr]
