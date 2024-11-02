from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol


@dataclass
class GenericCompArgumentNamedAst(Ast, Ordered, Stage4_SemanticAnalyser):
    name: TypeAst
    tok_assign: TokenAst
    value: ExpressionAst

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import TypeAst

        # Convert the name to a TypeAst.
        self.name = TypeAst.from_identifier(self.name)
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
    def from_name_value(name: TypeAst, value: ExpressionAst) -> GenericCompArgumentNamedAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TokenAst
        return GenericCompArgumentNamedAst(-1, IdentifierAst.from_type(name), TokenAst.default(TokenType.TkAssign), value)

    @staticmethod
    def from_symbol(symbol: VariableSymbol) -> GenericCompArgumentNamedAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TokenAst
        return GenericCompArgumentNamedAst(-1, symbol.name, TokenAst.default(TokenType.TkAssign), symbol.memory_info.ast_comptime_const)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.value)

        # Analyse the value of the named argument.
        self.value.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenericCompArgumentNamedAst"]
