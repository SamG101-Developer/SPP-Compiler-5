from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol


@dataclass
class GenericTypeArgumentNamedAst(Ast, Ordered):
    name: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAssign))
    value: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        # assert self.value
        self._variant = "Named"

    def __eq__(self, other: GenericTypeArgumentNamedAst) -> bool:
        # Check both ASTs are the same type and have the same name and value.
        return isinstance(other, GenericTypeArgumentNamedAst) and self.name == other.name and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.

        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    @staticmethod
    def from_symbol(symbol: TypeSymbol) -> GenericTypeArgumentNamedAst:
        value = symbol.scope.type_symbol.fq_name if symbol.scope else symbol.scope
        return GenericTypeArgumentNamedAst(name=Asts.TypeSingleAst.from_generic_identifier(symbol.name), value=value)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the name and value of the generic type argument.
        convention = self.value.get_convention()
        self.value.analyse_semantics(scope_manager, **kwargs)
        self.value = scope_manager.current_scope.get_symbol(self.value).fq_name

        if type(convention) is not Asts.ConventionMovAst:
            self.value = self.value.with_convention(convention)


__all__ = ["GenericTypeArgumentNamedAst"]
