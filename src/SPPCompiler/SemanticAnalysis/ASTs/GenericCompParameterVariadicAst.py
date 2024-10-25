from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericCompParameterVariadicAst(Ast, Stage2_SymbolGenerator):
    tok_cmp: TokenAst
    tok_variadic: TokenAst
    name: TypeAst
    tok_colon: TokenAst
    type: TypeAst

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import TypeAst

        # Convert the name to a TypeAst.
        self.name = TypeAst.from_identifier(self.name)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_cmp.print(printer) + " ",
            self.tok_variadic.print(printer),
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Create a variable symbol for this constant in the current scope (class / function).
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
        from SPPCompiler.SemanticAnalysis.Meta.AstVisbility import AstVisibility
        from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
        symbol = VariableSymbol(name=IdentifierAst.from_type(self.name), type=self.type, visibility=AstVisibility.Public)
        scope_manager.current_scope.add_symbol(symbol)


__all__ = ["GenericCompParameterVariadicAst"]
