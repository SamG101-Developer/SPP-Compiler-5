from __future__ import annotations
from typing import TYPE_CHECKING
from llvmlite import ir

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis import Asts
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol, TypeSymbol, VariableSymbol


class BuildTypes:
    _sm: ScopeManager

    def __init__(self, sm: ScopeManager) -> None:
        self._sm = sm

    def build(self) -> None:
        ...

    def _build_module(self, namespace: NamespaceSymbol, scope: Scope) -> ir.Module:
        from SPPCompiler.CodeGen.LlvmSymbolInfo import LlvmSymbolInfo

        # Create the LLVM module.
        module = ir.Module(name=str(namespace.name), context=ir.Context())
        namespace.llvm_info = LlvmSymbolInfo(llvm_type=None, llvm_module=module)
        return module

    def _assign_types_into_module(self, module: ir.Module, scope: Scope) -> None:
        # Fill the module with the class types.
        for type in scope.all_symbols(True).filter_to_type(TypeSymbol):
            self._build_type(module, type)

    def _assign_memory_layouts_into_module(self, module: ir.Module, scope: Scope) -> None:
        # Fill the module with the class memory layouts.
        for type in scope.all_symbols(True).filter_to_type(TypeSymbol):
            self._create_memory_layout(module, type)

    def _build_type(self, module: ir.Module, type: TypeSymbol) -> ir.IdentifiedStructType:
        from SPPCompiler.CodeGen.LlvmSymbolInfo import LlvmSymbolInfo

        # Create the LLVM type in the module, with no body (assigned in next stage).
        llvm_type_name = self._create_llvm_type_name(type.fq_name)
        llvm_type = module.context.get_identified_type(llvm_type_name)
        type.llvm_info = LlvmSymbolInfo(llvm_type=llvm_type, llvm_module=module)
        return llvm_type

    def _create_memory_layout(self, module: ir.Module, type: TypeSymbol) -> None:
        super_class_types = []
        for super_class in type.scope._direct_sup_scopes.filter(lambda s: isinstance(s._ast, Asts.ClassPrototypeAst)):
            super_class_types.append(super_class.type_symbol.llvm_info.llvm_type)

        attribute_types = []
        for attribute in type.scope.all_symbols(True).filter_to_type(VariableSymbol):
            attribute_types.append(attribute.type.llvm_info.llvm_type)

        # Set the body of the LLVM type.
        type.llvm_info.llvm_type.set_body(*super_class_types, *attribute_types)

    def _create_llvm_type_name(self, type: Asts.TypeAst) -> str:
        return f"{type}"


__all__ = ["BuildTypes"]
