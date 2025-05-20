from __future__ import annotations

import difflib
from dataclasses import dataclass, field

from convert_case import pascal_case

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import NamespaceSymbol, VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True)
class IdentifierAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    value: str = field(default="")

    def __deepcopy__(self, memodict=None) -> IdentifierAst:
        return IdentifierAst(pos=self.pos, value=self.value)

    def __eq__(self, other: IdentifierAst) -> bool:
        if isinstance(other, (IdentifierAst, Asts.GenericIdentifierAst)):
            return self.value == other.value
        elif isinstance(other, Asts.TypeSingleAst):
            return self.value == other.name.value
        else:
            return False

    def __hash__(self) -> int:
        # Hash the value into a fixed string and convert it into an integer.
        return hash(self.value)

    def __add__(self, other: IdentifierAst | str) -> IdentifierAst:
        if isinstance(other, str):
            self.value += other
        elif isinstance(other, IdentifierAst):
            self.value += other.value
        else:
            raise TypeError(f"Unsupported type for concatenation: {type(other)}")
        return self

    def __json__(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.value

    @property
    def pos_end(self) -> int:
        return self.pos + len(self.value)

    @staticmethod
    def from_type(type: Asts.TypeAst) -> Asts.IdentifierAst:
        return IdentifierAst.from_generic_identifier(type.type_parts[0])

    @staticmethod
    def from_generic_identifier(identifier: Asts.GenericIdentifierAst) -> IdentifierAst:
        return IdentifierAst(identifier.pos, identifier.value)

    def to_function_identifier(self) -> IdentifierAst:
        return IdentifierAst(pos=self.pos, value=f"${pascal_case(self.value.replace("_", " "))}")

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Extract the symbol from the current scope.
        symbol = sm.current_scope.get_symbol(self)

        # If the symbol is a variable, then get its type.
        if symbol.__class__ is VariableSymbol:
            return symbol.type

        # If the symbol is a namespace, then return "self" as the type.
        elif symbol.__class__ is NamespaceSymbol:
            return self

        else:
            raise ValueError(f"Symbol for {self} is not a variable or namespace.")

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check there is a symbol with the same name in the current scope.
        if not sm.current_scope.has_symbol(self):
            alternatives = [s.name.value for s in sm.current_scope.all_symbols() if s.__class__ is VariableSymbol]
            closest_match = difflib.get_close_matches(self.value, alternatives, n=1, cutoff=0)
            raise SemanticErrors.IdentifierUnknownError().add(
                self, "identifier", closest_match[0] if closest_match else None).scopes(sm.current_scope)


__all__ = [
    "IdentifierAst"]
