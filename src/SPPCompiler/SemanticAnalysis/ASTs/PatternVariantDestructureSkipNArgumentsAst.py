from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping


@dataclass
class PatternVariantDestructureSkipNArgumentsAst(Ast, PatternMapping):
    tok_variadic: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkDoubleDot))
    binding: Optional[Asts.PatternVariantSingleIdentifierAst] = field(default=None)

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
        return Asts.LocalVariableDestructureSkipNArgumentsAst(self.pos, self.tok_variadic, converted_binding)


__all__ = ["PatternVariantDestructureSkipNArgumentsAst"]
