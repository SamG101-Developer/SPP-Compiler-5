from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.FunctionCache import FunctionCache


@dataclass(slots=True, repr=False)
class TypeUnaryOperatorNamespaceAst(Asts.Ast):
    name: Asts.IdentifierAst = field(default=None)
    tok_dbl_colon: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.is_type_ast = True

    def __eq__(self, other: TypeUnaryOperatorNamespaceAst) -> bool:
        return self.name.value == other.name.value

    def __hash__(self) -> int:
        return hash(self.name.value)

    def __str__(self) -> str:
        return f"{self.name}::"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return f"{self.name.print(printer)}::"

    @FunctionCache.cache_property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.TypeIdentifierAst | Asts.TokenAst]:
        return [self.name]

    @FunctionCache.cache_property
    def namespace_parts(self) -> list[Asts.IdentifierAst]:
        return [self.name]

    @FunctionCache.cache_property
    def type_parts(self) -> list[Asts.TypeIdentifierAst | Asts.TokenAst]:
        return []

    @property
    def pos_end(self) -> int:
        return self.tok_dbl_colon.pos_end


__all__ = [
    "TypeUnaryOperatorNamespaceAst"]
