from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True)
class TypePostfixOperatorNestedTypeAst(Asts.Ast):
    tok_sep: Asts.TokenAst = field(default=None)
    name: Asts.TypeIdentifierAst = field(default=None)

    def __hash__(self) -> int:
        return hash(self.name)

    def __post_init__(self) -> None:
        self.tok_sep = self.tok_sep or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDoubleColon)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.tok_sep}{self.name}"

    @property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.TypeIdentifierAst | Asts.TokenAst]:
        return self.name.fq_type_parts

    @property
    def type_parts(self) -> list[Asts.TypeIdentifierAst]:
        return self.name.type_parts

    @property
    def pos_end(self) -> int:
        return self.name.pos_end


__all__ = [
    "TypePostfixOperatorNestedTypeAst"]
