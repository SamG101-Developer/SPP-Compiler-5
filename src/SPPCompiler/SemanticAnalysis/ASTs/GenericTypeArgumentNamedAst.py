from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
    from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol


@dataclass
class GenericTypeArgumentNamedAst(Ast, Ordered, Stage4_SemanticAnalyser):
    name: TypeAst
    tok_assign: TokenAst
    value: TypeAst

    def __post_init__(self) -> None:
        from SPPCompiler.SemanticAnalysis import TypeAst
        self._variant = "Named"
        self.name = TypeAst.from_identifier(self.name)

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

    @staticmethod
    def from_name_value(name: TypeAst, value: TypeAst) -> GenericTypeArgumentNamedAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TokenAst
        return GenericTypeArgumentNamedAst(-1, IdentifierAst.from_type(name), TokenAst.default(TokenType.TkAssign), value)

    @staticmethod
    def from_symbol(symbol: TypeSymbol) -> GenericTypeArgumentNamedAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TokenAst
        return GenericTypeArgumentNamedAst(-1, IdentifierAst.from_generic_identifier(symbol.name), TokenAst.default(TokenType.TkAssign), symbol.fq_name)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the name and value of the generic type argument.
        self.value.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenericTypeArgumentNamedAst"]
