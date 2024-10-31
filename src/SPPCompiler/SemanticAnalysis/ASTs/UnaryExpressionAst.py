from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.UnaryExpressionOperatorAst import UnaryExpressionOperatorAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class UnaryExpressionAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    op: UnaryExpressionOperatorAst
    rhs: ExpressionAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.op.print(printer),
            self.rhs.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type of the unary operation being applied to the "rhs".
        return self.op.infer_type(scope_manager, rhs=self.rhs, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the rhs.
        if isinstance(self.rhs, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.rhs)

        # Analyse the "op" and the "rhs".
        self.op.analyse_semantics(scope_manager, rhs=self.rhs, **kwargs)
        self.rhs.analyse_semantics(scope_manager, **kwargs)


__all__ = ["UnaryExpressionAst"]
