from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable


@dataclass
class TypePostfixOperatorOptionalTypeAst(Ast, TypeInferrable):
    tok_qst: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst())

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.tok_qst}"


__all__ = ["TypePostfixOperatorOptionalTypeAst"]
