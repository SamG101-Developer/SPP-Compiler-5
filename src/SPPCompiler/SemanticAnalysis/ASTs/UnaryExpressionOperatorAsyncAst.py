from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class UnaryExpressionOperatorAsyncAst(Ast, TypeInferrable):
    tok_async: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwAsync))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_async.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_async.pos_end

    def infer_type(self, scope_manager: ScopeManager, rhs: Asts.ExpressionAst = None, **kwargs) -> Asts.TypeAst:
        # Async calls wrap the return type in a future type.
        inner_type = rhs.infer_type(scope_manager)
        future_type = CommonTypes.Fut(inner_type, self.tok_async.pos)
        future_type.analyse_semantics(scope_manager)
        return future_type

    def analyse_semantics(self, scope_manager: ScopeManager, rhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # Check the rhs is a postfix function call.
        if not (isinstance(rhs, Asts.PostfixExpressionAst) and isinstance(rhs.op, Asts.PostfixExpressionOperatorFunctionCallAst)):
            raise SemanticErrors.AsyncFunctionCallInvalidTargetError().add(self, rhs).scopes(scope_manager.current_scope)

        # Mark the function call as async.
        rhs.op._is_async = self


__all__ = ["UnaryExpressionOperatorAsyncAst"]
