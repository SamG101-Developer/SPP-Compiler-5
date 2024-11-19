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
class PostfixExpressionOperatorNotKeywordAst(Ast, TypeInferrable, CompilerStages):
    tok_dot: TokenAst
    tok_not: TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_dot.print(printer),
            self.tok_not.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Not operations are always as "bool".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        bool_type = CommonTypes.Bool(self.pos)
        return InferredType.from_type(bool_type)

    def analyse_semantics(self, scope_manager: ScopeManager, lhs: ExpressionAst = None, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import AstErrors
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        
        # Check the loop condition is boolean.
        target_type = CommonTypes.Bool(self.pos)
        return_type = lhs.infer_type(scope_manager).type
        if not target_type.symbolic_eq(return_type, scope_manager.current_scope):
            raise AstErrors.CONDITION_NOT_BOOLEAN(lhs, return_type, "not expression")


__all__ = ["PostfixExpressionOperatorNotKeywordAst"]
