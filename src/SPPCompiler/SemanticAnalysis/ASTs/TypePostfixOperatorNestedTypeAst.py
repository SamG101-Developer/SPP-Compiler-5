from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class TypePostfixOperatorNestedTypeAst(Ast):
    tok_dbl_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())
    name: Asts.TypeSingleAst = field(default_factory=lambda: Asts.TypeSingleAst())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.tok_dbl_colon}{self.name}"

    def fq_type_parts(self) -> Seq[Asts.IdentifierAst | Asts.GenericIdentifierAst | Asts.TokenAst]:
        return self.name.fq_type_parts()

    def type_parts(self) -> Seq[Asts.GenericIdentifierAst]:
        return self.name.type_parts()


__all__ = ["TypePostfixOperatorNestedTypeAst"]
