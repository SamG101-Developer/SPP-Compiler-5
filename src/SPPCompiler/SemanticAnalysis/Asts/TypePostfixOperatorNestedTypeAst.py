from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.FunctionCache import FunctionCache


@dataclass(slots=True, repr=False)
class TypePostfixOperatorNestedTypeAst(Asts.Ast):
    tok_sep: Asts.TokenAst = field(default=None)
    name: Asts.TypeIdentifierAst = field(default=None)

    def __post_init__(self) -> None:
        self.is_type_ast = True

    def __hash__(self) -> int:
        return hash(self.name.value)

    def __str__(self) -> str:
        # Return the string representation of the nested type.
        string = ["::", str(self.name)]
        return "".join(string)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = ["::", self.name.print(printer)]
        return "".join(string)

    @FunctionCache.cache_property
    def fq_type_parts(self) -> list[Asts.IdentifierAst | Asts.TypeIdentifierAst | Asts.TokenAst]:
        return self.name.fq_type_parts

    @FunctionCache.cache_property
    def type_parts(self) -> list[Asts.TypeIdentifierAst | Asts.TokenAst]:
        return self.name.type_parts

    @property
    def pos_end(self) -> int:
        return self.name.pos_end


__all__ = [
    "TypePostfixOperatorNestedTypeAst"]
