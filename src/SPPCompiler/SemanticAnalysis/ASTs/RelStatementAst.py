from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class RelStatementAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_rel: TokenAst
    expressions: Seq[ExpressionAst]

    def __post_init__(self) -> None:
        # Convert the expressions into a sequence.
        self.expressions = Seq(self.expressions)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_rel.print(printer) + " ",
            self.expressions.print(printer, ", ")]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # All statements are inferred as "void".
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        void_type = CommonTypes.Void(self.pos)
        return InferredType.from_type(void_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.expressions.for_each(lambda expression: expression.analyse_semantics(scope_manager, **kwargs))


__all__ = ["RelStatementAst"]
