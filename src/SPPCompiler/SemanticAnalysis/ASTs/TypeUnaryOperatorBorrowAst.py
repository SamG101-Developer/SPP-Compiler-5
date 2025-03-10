from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable


@dataclass
class TypeUnaryOperatorBorrowAst(Ast, TypeInferrable):
    convention: Asts.ConventionAst = field(default_factory=lambda: Asts.IdentifierAst())

    def __eq__(self, other: TypeUnaryOperatorBorrowAst) -> bool:
        return type(self.convention) is type(other.convention)

    def __hash__(self) -> int:
        return hash(str(self.convention))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.convention.print(printer)


__all__ = ["TypeUnaryOperatorBorrowAst"]
