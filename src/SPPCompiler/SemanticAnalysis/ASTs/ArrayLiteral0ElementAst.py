from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ArrayLiteral0ElementAst(Ast, TypeInferrable, Stage4_SemanticAnalyser):
    tok_left_bracket: TokenAst
    element_type: TypeAst
    tok_comma: TokenAst
    size: TokenAst
    tok_right_bracket: TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_left_bracket.print(printer),
            self.element_type.print(printer),
            self.tok_comma.print(printer) + " ",
            self.size.print(printer),
            self.tok_right_bracket.print(printer)]
        return " ".join(string)

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Create the standard "std::Arr[T, n: BigNum]" type, with generic items.
        from SPPCompiler.SemanticAnalysis import IntegerLiteralAst

        # Create the size literal, and use the provided element type.
        size = IntegerLiteralAst.from_token(self.size, self.size.pos)
        array_type = CommonTypes.Arr(self.element_type, size, self.pos)
        array_type.analyse_semantics(scope_manager, **kwargs)
        return InferredType.from_type(array_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.element_type.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ArrayLiteral0ElementAst"]
