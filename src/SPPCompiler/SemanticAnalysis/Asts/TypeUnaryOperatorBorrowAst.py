from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True)
class TypeUnaryOperatorBorrowAst(Asts.Ast):
    convention: Asts.ConventionAst = field(default=None)

    def __eq__(self, other: TypeUnaryOperatorBorrowAst) -> bool:
        return type(self.convention) is type(other.convention)

    def __hash__(self) -> int:
        return hash(self.convention)

    def __str__(self) -> str:
        return str(self.convention)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.convention.print(printer)

    @property
    def pos_end(self) -> int:
        return self.convention.pos_end

    @property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.TypeIdentifierAst | Asts.TokenAst]:
        return []

    @property
    def namespace_parts(self) -> list[Asts.IdentifierAst]:
        return []

    @property
    def type_parts(self) -> list[Asts.TypeIdentifierAst | Asts.TokenAst]:
        return []


__all__ = [
    "TypeUnaryOperatorBorrowAst"]
