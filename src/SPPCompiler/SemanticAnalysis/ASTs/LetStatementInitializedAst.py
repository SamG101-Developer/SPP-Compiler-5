from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LetStatementInitializedAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    let_keyword: TokenAst
    assign_to: LocalVariableAst
    assign_token: TokenAst
    value: ExpressionAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.let_keyword.print(printer) + " ",
            self.assign_to.print(printer) + " ",
            self.assign_token.print(printer) + " ",
            self.value.print(printer)]
        return "".join(string)

    @staticmethod
    def from_variable_and_value(variable: LocalVariableAst, value: ExpressionAst) -> LetStatementInitializedAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import TokenAst
        return LetStatementInitializedAst(-1, TokenAst.default(TokenType.KwLet), variable, TokenAst.default(TokenType.TkAssign), value)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.value)

        # Analyse the assign_to and value of the let statement.
        self.value.analyse_semantics(scope_manager, **kwargs)
        self.assign_to.analyse_semantics(scope_manager, value=self.value, **kwargs)


__all__ = ["LetStatementInitializedAst"]
