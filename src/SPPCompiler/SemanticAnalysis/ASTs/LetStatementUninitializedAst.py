from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class LetStatementUninitializedAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_let: TokenAst
    tok_assign: LocalVariableAst
    tok_colon: TokenAst
    type: TypeAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = [
            self.tok_let.print(printer) + " ",
            self.tok_assign.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer)]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        ...

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.type.analyse_semantics(scope_manager, **kwargs)


__all__ = ["LetStatementUninitializedAst"]
