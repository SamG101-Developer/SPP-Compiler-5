from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantSingleIdentifierAst import PatternVariantSingleIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureSkipNArgumentsAst import LocalVariableDestructureSkipNArgumentsAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantDestructureSkipNArgumentsAst(Ast, PatternMapping, TypeInferrable, Stage4_SemanticAnalyser):
    variadic_token: TokenAst
    binding: Optional[PatternVariantSingleIdentifierAst]

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variadic_token.print(printer),
            self.binding.print(printer) if self.binding is not None else ""]
        return "".join(string)

    def convert_to_variable(self, **kwargs) -> LocalVariableDestructureSkipNArgumentsAst:
        ...

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        ...

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["PatternVariantDestructureSkipNArgumentsAst"]
