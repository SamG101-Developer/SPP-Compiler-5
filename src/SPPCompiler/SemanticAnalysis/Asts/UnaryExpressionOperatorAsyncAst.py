from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class UnaryExpressionOperatorAsyncAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_async: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwAsync))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return f"{self.tok_async.print(printer)} "

    @property
    def pos_end(self) -> int:
        return self.tok_async.pos_end

    def infer_type(self, sm: ScopeManager, rhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # Async calls wrap the return type in a future type.
        inner_type = rhs.infer_type(sm, **kwargs)
        future_type = CommonTypes.Fut(self.tok_async.pos, inner_type)
        future_type.analyse_semantics(sm, **kwargs)
        return future_type

    def analyse_semantics(self, sm: ScopeManager, rhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # Check the rhs is a postfix function call.
        if not (type(rhs) is Asts.PostfixExpressionAst and type(rhs.op) is Asts.PostfixExpressionOperatorFunctionCallAst):
            raise SemanticErrors.AsyncFunctionCallInvalidTargetError().add(
                self, rhs).scopes(sm.current_scope)

        # Mark the function call as async.
        rhs.op._is_async = self


__all__ = [
    "UnaryExpressionOperatorAsyncAst"]
