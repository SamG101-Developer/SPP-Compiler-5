from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method


@dataclass(slots=True, repr=False)
class PatternVariantDestructureSkipNArgumentsAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    tok_variadic: Asts.TokenAst = field(default=None)
    binding: Optional[Asts.PatternVariantSingleIdentifierAst] = field(default=None)

    def __str__(self) -> str:
        # String representation of the AST.
        return f"{self.tok_variadic}{self.binding if self.binding else ""}"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_variadic.print(printer),
            self.binding.print(printer) if self.binding is not None else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.binding.pos_end if self.binding else self.tok_variadic.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableDestructureSkipNArgumentsAst:
        # Convert the skip n arguments destructuring into a local variable skip n arguments destructuring.
        converted_binding = self.binding.convert_to_variable(**kwargs) if self.binding else None
        variable = Asts.LocalVariableDestructureSkipNArgumentsAst(self.pos, self.tok_variadic, converted_binding)
        variable._from_pattern = True
        return variable


__all__ = [
    "PatternVariantDestructureSkipNArgumentsAst"]
