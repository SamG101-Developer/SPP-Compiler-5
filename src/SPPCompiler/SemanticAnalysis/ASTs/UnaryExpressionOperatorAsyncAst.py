from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class UnaryExpressionOperatorAsyncAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_async: TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_async.print(printer)

    def infer_type(self, scope_manager: ScopeManager, rhs: ExpressionAst = None, **kwargs) -> InferredType:
        # Async calls wrap the return type in a future type.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        inner_type = rhs.infer_type(scope_manager).type
        future_type = CommonTypes.Fut(inner_type)
        future_type.analyse_semantics(scope_manager)
        return InferredType.from_type(future_type)

    def analyse_semantics(self, scope_manager: ScopeManager, rhs: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import PostfixExpressionAst, PostfixExpressionOperatorFunctionCallAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # Check the rhs is a postfix function call.
        if not (isinstance(rhs, PostfixExpressionAst) and isinstance(rhs.op, PostfixExpressionOperatorFunctionCallAst)):
            raise AstErrors.INVALID_ASYNC_TARGET(self.pos, rhs)

        # Mark the function call as async.
        rhs.op._is_async = self


__all__ = ["UnaryExpressionOperatorAsyncAst"]
