from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ParenthesizedExpressionAst(Ast, TypeInferrable, CompilerStages):
    tok_left_paren: TokenAst
    expression: ExpressionAst
    tok_right_paren: TokenAst

    @staticmethod
    def from_expression(expression: ExpressionAst, *, pos: int = -1) -> ParenthesizedExpressionAst:
        from SPPCompiler.SemanticAnalysis import TokenAst
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        return ParenthesizedExpressionAst(pos, TokenAst.default(TokenType.TkParenL), expression, TokenAst.default(TokenType.TkParenR))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_paren.print(printer),
            self.expression.print(printer),
            self.tok_right_paren.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type of the expression.
        return self.expression.infer_type(scope_manager, **kwargs)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the expression.
        if isinstance(self.expression, (TokenAst, TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.expression)

        # Analyse the expression.
        self.expression.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ParenthesizedExpressionAst"]
