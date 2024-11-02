from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ObjectInitializerArgumentNamedAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    name: IdentifierAst | TokenAst
    assignment_token: TokenAst
    value: ExpressionAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.assignment_token.print(printer),
            self.value.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type of the value of the argument.
        return self.value.infer_type(scope_manager, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.value)

        # Analyse the value of the argument.
        self.value.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ObjectInitializerArgumentNamedAst"]
