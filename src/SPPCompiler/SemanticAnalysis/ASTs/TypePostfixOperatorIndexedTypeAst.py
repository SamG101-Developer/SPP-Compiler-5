from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypePostfixOperatorIndexedTypeAst(Ast):
    tok_dbl_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())
    index: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.tok_dbl_colon}{self.index}"

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return Seq([self.index])

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        return Seq([self.index])


__all__ = ["TypePostfixOperatorIndexedTypeAst"]
