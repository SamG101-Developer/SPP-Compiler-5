from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True)
class TypePostfixOperatorOptionalTypeAst(Asts.Ast):
    tok_qst: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.tok_qst}"

    @property
    def pos_end(self) -> int:
        return self.tok_qst.pos_end


__all__ = [
    "TypePostfixOperatorOptionalTypeAst"]
