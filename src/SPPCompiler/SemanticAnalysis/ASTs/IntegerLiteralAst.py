from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class IntegerLiteralAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_sign: Optional[TokenAst]
    value: TokenAst
    type: Optional[TypeAst]

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst

        # Convert the name to a TypeAst.
        self.type = TypeAst.from_identifier(self.type) if self.type else None

    def __eq__(self, other: IntegerLiteralAst) -> bool:
        # Check both ASTs are the same type and have the same sign, value and type.
        return isinstance(other, IntegerLiteralAst) and self.tok_sign == other.tok_sign and int(self.value.token.token_metadata) == int(other.value.token.token_metadata) and self.type == other.type

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sign.print(printer) if self.tok_sign else "",
            self.value.print(printer),
            self.type.print(printer) if self.type else ""]
        return " ".join(string)

    @functools.cache
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        ...

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["IntegerLiteralAst"]
