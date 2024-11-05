from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionCallArgumentUnnamedAst(Ast, Ordered, TypeInferrable, Stage4_SemanticAnalyser):
    convention: ConventionAst
    tok_unpack: Optional[TokenAst]
    value: ExpressionAst

    def __post_init__(self) -> None:
        self._variant = "Unnamed"

    def __eq__(self, other: FunctionCallArgumentUnnamedAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return isinstance(other, FunctionCallArgumentUnnamedAst) and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.convention.print(printer),
            self.tok_unpack.print(printer) if self.tok_unpack is not None else "",
            self.value.print(printer)]
        return "".join(string)

    @staticmethod
    def from_value(value: ExpressionAst) -> FunctionCallArgumentUnnamedAst:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst
        return FunctionCallArgumentUnnamedAst(-1, ConventionMovAst.default(), None, value)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst
        inferred_type = self.value.infer_type(scope_manager, **kwargs)

        # The convention is either from the convention attribute or the symbol information.
        match self.convention, inferred_type.convention:
            case ConventionMovAst(), symbol_convention: convention = symbol_convention
            case _: convention = type(self.convention)
        return InferredType(convention=convention, type=inferred_type.type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstErrors import AstErrors

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (TokenAst, TypeAst)):
            raise AstErrors.INVALID_EXPRESSION(self.value)

        self.value.analyse_semantics(scope_manager, **kwargs)


__all__ = ["FunctionCallArgumentUnnamedAst"]
