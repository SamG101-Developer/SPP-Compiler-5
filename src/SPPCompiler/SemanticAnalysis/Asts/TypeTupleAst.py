from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes


@dataclass(slots=True, repr=False)
class TypeTupleAst(Asts.Ast, Asts.Mixins.AbstractTypeTemporaryAst):
    tok_l: Asts.TokenAst = field(default=None)
    type_elems: list[Asts.TypeAst] = field(default_factory=list)
    tok_r: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_l = self.tok_l or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkLeftParenthesis)
        self.tok_r = self.tok_r or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkRightParenthesis)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return ""

    @property
    def pos_end(self) -> int:
        return self.tok_r.pos_end

    def convert(self) -> Asts.TypeAst:
        return CommonTypes.Tup(self.pos, self.type_elems)


__all__ = [
    "TypeTupleAst"]
