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
class PostfixExpressionOperatorNotKeywordAst(Ast, TypeInferrable):
    tok_dot: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkDot))
    tok_not: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwNot))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_dot.print(printer),
            self.tok_not.print(printer)]
        return "".join(string)

    def is_runtime_access(self) -> bool:
        return True

    def is_static_access(self) -> bool:
        return False

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Not operations are always as "bool".
        return CommonTypes.Bool(self.pos)

    def analyse_semantics(self, scope_manager: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # Check the loop condition is boolean.
        target_type = CommonTypes.Bool(self.pos)
        return_type = lhs.infer_type(scope_manager)
        if not target_type.symbolic_eq(return_type, scope_manager.current_scope):
            raise SemanticErrors.ExpressionNotBooleanError().add(lhs, return_type, "not expression")


__all__ = ["PostfixExpressionOperatorNotKeywordAst"]
