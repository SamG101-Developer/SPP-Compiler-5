from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes


@dataclass
class TypeArrayAst(Asts.Ast, Asts.Mixins.AbstractTypeTemporaryAst):
    tok_l: Asts.TokenAst = field(default=None)
    elem_type: Asts.TypeAst = field(default=None)
    comma: Asts.TokenAst = field(default=None)
    size: Asts.TokenAst = field(default=None)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftSquareBracket)
        self.comma = self.comma or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkComma)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightSquareBracket)
        assert self.elem_type is not None and self.size is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return ""

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def convert(self) -> Asts.TypeAst:
        return CommonTypes.Arr(self.pos, self.elem_type, self.size)


__all__ = [
    "TypeArrayAst"]
