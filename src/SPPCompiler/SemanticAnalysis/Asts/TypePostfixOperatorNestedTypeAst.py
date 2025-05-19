from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True)
class TypePostfixOperatorNestedTypeAst(Asts.Ast):
    tok_sep: Asts.TokenAst = field(default=None)
    name: Asts.TypeSingleAst = field(default=None)

    def __hash__(self) -> int:
        return hash(self.name)

    def __post_init__(self) -> None:
        self.tok_sep = self.tok_sep or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDoubleColon)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.tok_sep}{self.name}"

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    def fq_type_parts(self) -> List[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return self.name.fq_type_parts()

    def type_parts(self) -> List[Asts.GenericIdentifierAst]:
        return self.name.type_parts()


__all__ = [
    "TypePostfixOperatorNestedTypeAst"]
