from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypeUnaryOperatorNamespaceAst(Asts.Ast):
    name: Asts.IdentifierAst = field(default=None)
    tok_dbl_colon: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_dbl_colon = self.tok_dbl_colon or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDoubleColon)
        assert self.name is not None

    def __eq__(self, other: TypeUnaryOperatorNamespaceAst) -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.name}{self.tok_dbl_colon}"

    @property
    def pos_end(self) -> int:
        return self.tok_dbl_colon.pos_end

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return Seq([self.name])

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        return Seq()


__all__ = [
    "TypeUnaryOperatorNamespaceAst"]
