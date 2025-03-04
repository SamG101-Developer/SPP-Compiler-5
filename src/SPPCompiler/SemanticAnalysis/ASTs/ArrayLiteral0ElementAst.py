from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ArrayLiteral0ElementAst(Ast, TypeInferrable):
    tok_left_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkLeftSquareBracket))
    element_type: Asts.TypeAst = field(default=None)
    tok_comma: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkComma))
    size: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.LxNumber))
    tok_right_bracket: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkRightSquareBracket))

    def __post_init__(self) -> None:
        assert self.element_type

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

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        # Create the standard "std::Arr[T, n: BigNum]" type, with generic items.
        size = Asts.IntegerLiteralAst.from_token(self.size, self.size.pos)
        array_type = CommonTypes.Arr(self.element_type, size, self.pos)
        array_type.analyse_semantics(scope_manager, **kwargs)
        return InferredTypeInfo(array_type)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        self.element_type.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ArrayLiteral0ElementAst"]
