from dataclasses import dataclass
from llvmlite import ir
from typing import Optional


@dataclass(kw_only=True)
class LlvmSymbolInfo:
    llvm_type: Optional[ir.IdentifiedStructType]
    llvm_module: ir.Module


__all__ = ["LlvmSymbolInfo"]
