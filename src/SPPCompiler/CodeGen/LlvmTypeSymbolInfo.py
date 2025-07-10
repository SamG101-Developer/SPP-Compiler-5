from dataclasses import dataclass

from llvmlite import ir


@dataclass(slots=True, kw_only=True)
class LlvmTypeSymbolInfo:
    llvm_type: ir.IdentifiedStructType
    llvm_module: ir.Module
