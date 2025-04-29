from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class TypeUnaryOperatorNamespaceAst(Asts.Ast):
    name: Asts.IdentifierAst = field(default=None)
    tok_dbl_colon: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_dbl_colon = self.tok_dbl_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDoubleColon)

    def __eq__(self, other: TypeUnaryOperatorNamespaceAst) -> bool:
        return self.name.value == other.name.value

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return f"{self.name}{self.tok_dbl_colon}"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.name.print(printer)}{self.tok_dbl_colon.print(printer)}"

    @property
    def pos_end(self) -> int:
        return self.tok_dbl_colon.pos_end

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return [self.name]

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        return []


__all__ = [
    "TypeUnaryOperatorNamespaceAst"]
