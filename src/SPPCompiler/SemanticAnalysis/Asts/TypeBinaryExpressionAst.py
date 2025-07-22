from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes


@dataclass(slots=True, repr=False)
class TypeBinaryExpressionAst(Asts.Ast, Asts.Mixins.AbstractTypeTemporaryAst):
    lhs: Asts.TypeAst = field(default=None)
    op: Asts.TokenAst = field(default=None)
    rhs: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.op = self.op or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.NoToken)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return ""

    @property
    def pos_end(self) -> int:
        return self.rhs.pos_end

    def convert(self) -> Asts.TypeAst:
        match self.op.token_type:
            case SppTokenType.KwOr:
                return CommonTypes.Var(self.pos, [self.lhs, self.rhs])
            case _:
                raise Exception(f"Invalid binary operator '{self.op.token_type}'")


__all__ = [
    "TypeBinaryExpressionAst"]
