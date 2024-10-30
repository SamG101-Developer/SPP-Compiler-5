from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableSingleIdentifierAst import LocalVariableSingleIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst


@dataclass
class PatternVariantSingleIdentifierAst(Ast, PatternMapping, Stage4_SemanticAnalyser):
    mut_tok: Optional[TokenAst]
    name: IdentifierAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.mut_tok.print(printer) if self.mut_tok is not None else "",
            self.name.print(printer)]
        return " ".join(string)

    def convert_to_variable(self, **kwargs) -> LocalVariableSingleIdentifierAst:
        # Convert the single identifier into a local variable single identifier.
        from SPPCompiler.SemanticAnalysis import LocalVariableSingleIdentifierAst
        return LocalVariableSingleIdentifierAst(self.pos, self.mut_tok, self.name)

    def analyse_semantics(self, scope_manager: ScopeManager, condition: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import LetStatementInitializedAst

        # Create the new variable from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        new_ast = LetStatementInitializedAst.from_variable_and_value(variable, condition)
        new_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantSingleIdentifierAst"]
