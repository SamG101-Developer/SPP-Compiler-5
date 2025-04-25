from dataclasses import dataclass, field
# from llvmlite import ir
from typing import Optional


# @dataclass(slots=True)(kw_only=True)
class LlvmSymbolInfo:
    ...
    # llvm_type: Optional[ir.IdentifiedStructType] = field(default=None)
    # llvm_module: ir.Module = field(default=None)


__all__ = ["LlvmSymbolInfo"]
