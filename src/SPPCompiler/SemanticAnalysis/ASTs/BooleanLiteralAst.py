from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class BooleanLiteralAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    value: TokenAst

    def __eq__(self, other: BooleanLiteralAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Create the standard "std::Bool" type.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        boolean_type = CommonTypes.Bool(self.pos)
        return InferredType.from_type(boolean_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["BooleanLiteralAst"]
