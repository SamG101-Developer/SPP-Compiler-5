from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import difflib, hashlib, warnings

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericIdentifierAst import GenericIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class IdentifierAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    value: str

    def __eq__(self, other: IdentifierAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return isinstance(other, IdentifierAst) and self.value == other.value

    def __hash__(self) -> int:
        # Hash the value into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.md5(self.value.encode()).digest())

    def __json__(self) -> str:
        # Return the internal string as the JSON formatted IdentifierAst.
        return self.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the internal string.
        return self.value

    @staticmethod
    def from_type(type: TypeAst) -> IdentifierAst:
        if type.namespace or type.types.length > 1:
            warnings.warn(f"Type {type} has a namespace or nested types, which will be ignored.")
        return IdentifierAst.from_generic_identifier(type.types[-1])

    @staticmethod
    def from_generic_identifier(identifier: GenericIdentifierAst) -> IdentifierAst:
        if identifier.generic_argument_group.arguments:
            warnings.warn(f"Generic identifier {identifier} has generic arguments, which will be ignored.")
        return IdentifierAst(identifier.pos, identifier.value)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol, VariableSymbol

        # Extract the symbol from the current scope.
        symbol = scope_manager.current_scope.get_symbol(self)

        # If the symbol is a variable, then get its type.
        if isinstance(symbol, VariableSymbol):
            return InferredType(symbol.memory_info.convention, symbol.type)

        # If the symbol is a namespace, then return "self" as the type.
        elif isinstance(symbol, NamespaceSymbol):
            return InferredType.from_type(self)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Check there is a symbol with the same name in the current scope.
        if not scope_manager.current_scope.has_symbol(self):
            alternatives = scope_manager.current_scope.all_symbols().filter_to_type(VariableSymbol).map_attr("name")
            closest_match = difflib.get_close_matches(self.value, alternatives.map_attr("value"), n=1, cutoff=0)
            raise AstErrors.UNDEFINED_IDENTIFIER(self, closest_match[0] if closest_match else None)


__all__ = ["IdentifierAst"]
