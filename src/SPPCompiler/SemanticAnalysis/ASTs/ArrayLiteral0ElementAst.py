from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Meta.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ArrayLiteral0ElementAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_left_bracket: TokenAst
    type: TypeAst
    tok_comma: TokenAst
    size: TokenAst
    tok_right_bracket: TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_bracket.print(printer),
            self.type.print(printer),
            self.tok_comma.print(printer) + " ",
            self.size.print(printer),
            self.tok_right_bracket.print(printer)]
        return " ".join(string)

    @functools.cache
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        from SPPCompiler.SemanticAnalysis import IntegerLiteralAst

        # Create an array type with the given size and element type.
        size = IntegerLiteralAst.from_token(self.size, self.size.pos)
        element_type = self.type
        array_type = CommonTypes.Arr(element_type, size, self.pos)
        return array_type

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.type.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ArrayLiteral0ElementAst"]
