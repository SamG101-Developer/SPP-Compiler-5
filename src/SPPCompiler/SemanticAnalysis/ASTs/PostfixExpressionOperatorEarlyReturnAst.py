from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PostfixExpressionOperatorEarlyReturnAst(Ast, TypeInferrable):
    tok_qst: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkQuestionMark))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_qst.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_qst.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        raise NotImplementedError("PostfixExpressionOperatorEarlyReturnAst not implemented yet")


__all__ = ["PostfixExpressionOperatorEarlyReturnAst"]
