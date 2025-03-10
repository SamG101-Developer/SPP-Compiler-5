from __future__ import annotations

from dataclasses import dataclass, field


import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol


@dataclass
class GenericCompArgumentNamedAst(Ast, Ordered):
    name: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAssign))
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        # assert self.value
        self._variant = "Named"

    def __eq__(self, other: GenericCompArgumentNamedAst) -> bool:
        # Check both ASTs are the same type and have the same name and value.
        return isinstance(other, GenericCompArgumentNamedAst) and self.name == other.name and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.value.print(printer)]
        return " ".join(string)

    @staticmethod
    def from_symbol(symbol: VariableSymbol) -> GenericCompArgumentNamedAst:
        return GenericCompArgumentNamedAst(name=Asts.TypeSingleAst.from_identifier(symbol.name), value=symbol.memory_info.ast_comptime_const)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value).scopes(scope_manager.current_scope)

        # Analyse the value of the named argument.
        self.value.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenericCompArgumentNamedAst"]
