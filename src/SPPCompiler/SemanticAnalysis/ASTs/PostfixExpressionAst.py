from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.PostfixExpressionOperatorAst import PostfixExpressionOperatorAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PostfixExpressionAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    lhs: ExpressionAst
    op: PostfixExpressionOperatorAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.lhs.print(printer),
            self.op.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type of the postfix operation being applied to the "lhs".
        return self.op.infer_type(scope_manager, lhs=self.lhs, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # The ".." TokenAst cannot be used as an expression for the lhs.
        if isinstance(self.lhs, TokenAst):
            raise AstErrors.INVALID_EXPRESSION(self.lhs)

        # Analyse the "lhs" and "op".
        self.lhs.analyse_semantics(scope_manager, **kwargs)
        self.op.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PostfixExpressionAst"]
