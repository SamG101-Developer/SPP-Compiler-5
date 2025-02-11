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
class GenericTypeParameterVariadicAst(Ast, Ordered):
    tok_variadic: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkDblDot))
    name: Asts.TypeAst = field(default=None)
    constraints: Asts.GenericTypeParameterInlineConstraintsAst = field(default_factory=lambda: Asts.GenericTypeParameterInlineConstraintsAst())

    def __post_init__(self) -> None:
        assert self.name
        self._variant = "Variadic"

    def __eq__(self, other: GenericTypeParameterVariadicAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericTypeParameterVariadicAst) and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_variadic.print(printer),
            self.name.print(printer),
            self.constraints.print(printer)]
        return "".join(string)

    def generate_top_level_scopes(self, scope_manager: ScopeManager) -> None:
        # Create a type symbol for this type in the current scope (class / function).
        symbol = TypeSymbol(name=self.name.types[-1], type=None, is_generic=True)
        scope_manager.current_scope.add_symbol(symbol)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.name.analyse_semantics(scope_manager, **kwargs)
        self.constraints.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenericTypeParameterVariadicAst"]
