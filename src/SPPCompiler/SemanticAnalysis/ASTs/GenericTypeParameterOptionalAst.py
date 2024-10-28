from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericTypeParameterInlineConstraintsAst import GenericTypeParameterInlineConstraintsAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericTypeParameterOptionalAst(Ast, Stage2_SymbolGenerator, Stage4_SemanticAnalyser):
    name: TypeAst
    constraints: GenericTypeParameterInlineConstraintsAst
    tok_assign: TokenAst
    default: TypeAst

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import TypeAst, GenericTypeParameterInlineConstraintsAst

        # Convert the name to a TypeAst, and create defaults.
        self.name = TypeAst.from_identifier(self.name)
        self.constraints = self.constraints or GenericTypeParameterInlineConstraintsAst.default()

    def __eq__(self, other: GenericTypeParameterOptionalAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericTypeParameterOptionalAst) and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.constraints.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        # Create a type symbol for this type in the current scope (class / function).
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
        symbol = TypeSymbol(name=self.name.types[-1], type=None, is_generic=True)
        scope_manager.current_scope.add_symbol(symbol)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.name.analyse_semantics(scope_manager, **kwargs)
        self.constraints.analyse_semantics(scope_manager, **kwargs)
        self.default.analyse_semantics(scope_manager, **kwargs)


__all__ = ["GenericTypeParameterOptionalAst"]
