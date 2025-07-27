from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.FunctionCache import FunctionCache


@dataclass(slots=True, repr=False)
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

    @FunctionCache.cache_property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.TypeIdentifierAst | Asts.TokenAst]:
        return []

    @FunctionCache.cache_property
    def namespace_parts(self) -> list[Asts.IdentifierAst]:
        return []

    @FunctionCache.cache_property
    def type_parts(self) -> list[Asts.TypeIdentifierAst | Asts.TokenAst]:
        return []


__all__ = [
    "TypeUnaryOperatorBorrowAst"]
