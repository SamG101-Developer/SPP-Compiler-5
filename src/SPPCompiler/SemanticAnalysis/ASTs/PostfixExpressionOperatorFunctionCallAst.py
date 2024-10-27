from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionCallArgumentGroupAst import FunctionCallArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.FunctionPrototypeAst import FunctionPrototypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericArgumentGroupAst import GenericArgumentGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PostfixExpressionOperatorFunctionCallAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    generic_argument_group: GenericArgumentGroupAst
    function_argument_group: FunctionCallArgumentGroupAst
    fold_token: Optional[TokenAst]

    _overload: Optional[FunctionPrototypeAst] = field(default=None, init=False, repr=False)
    _is_async: Optional[Ast] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import FunctionCallArgumentGroupAst, GenericArgumentGroupAst#

        # Create defaults.
        self.generic_argument_group = self.generic_argument_group or GenericArgumentGroupAst.default()
        self.function_argument_group = self.function_argument_group or FunctionCallArgumentGroupAst.default()

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.generic_argument_group.print(printer),
            self.function_argument_group.print(printer),
            self.fold_token.print(printer) if self.fold_token else ""]
        return "".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        ...

    def analyse_semantics(self, scope_handler: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["PostfixExpressionOperatorFunctionCallAst"]
