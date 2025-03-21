from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class PostfixExpressionOperatorEarlyReturnAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    tok_qst: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_qst = self.tok_qst or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkQuestionMark)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_qst.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_qst.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        raise NotImplementedError("PostfixExpressionOperatorEarlyReturnAst not implemented yet")


__all__ = [
    "PostfixExpressionOperatorEarlyReturnAst"]
