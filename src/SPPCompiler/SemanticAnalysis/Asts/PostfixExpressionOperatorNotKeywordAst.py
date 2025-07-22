from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


# todo: check memory w lhs here


@dataclass(slots=True, repr=False)
class PostfixExpressionOperatorNotKeywordAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_dot: Asts.TokenAst = field(default=None)
    tok_not: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_dot = Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDot)
        self.tok_not = Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwNot)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_dot.print(printer),
            self.tok_not.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.tok_not.pos_end

    def is_runtime_access(self) -> bool:
        return True

    def is_static_access(self) -> bool:
        return False

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Not operations are always as "bool".
        return CommonTypes.Bool(self.pos)

    def analyse_semantics(self, sm: ScopeManager, lhs: Asts.ExpressionAst = None, **kwargs) -> None:
        # Check the loop condition is boolean.
        target_type = CommonTypes.Bool(self.pos)
        return_type = lhs.infer_type(sm, **kwargs)
        if not AstTypeUtils.symbolic_eq(target_type, return_type, sm.current_scope, sm.current_scope):
            raise SemanticErrors.ExpressionNotBooleanError().add(
                lhs, return_type, "not expression").scopes(sm.current_scope)


__all__ = [
    "PostfixExpressionOperatorNotKeywordAst"]
