from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantSingleIdentifierAst import PatternVariantSingleIdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureSkipNArgumentsAst import LocalVariableDestructureSkipNArgumentsAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class PatternVariantDestructureSkipNArgumentsAst(Ast, PatternMapping):
    tok_variadic: TokenAst
    binding: Optional[PatternVariantSingleIdentifierAst]

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_variadic.print(printer),
            self.binding.print(printer) if self.binding is not None else ""]
        return "".join(string)

    def convert_to_variable(self, **kwargs) -> LocalVariableDestructureSkipNArgumentsAst:
        from SPPCompiler.SemanticAnalysis import LocalVariableDestructureSkipNArgumentsAst

        # Convert the skip n arguments destructuring into a local variable skip n arguments destructuring.
        converted_binding = self.binding.convert_to_variable(**kwargs) if self.binding else None
        return LocalVariableDestructureSkipNArgumentsAst(self.pos, self.tok_variadic, converted_binding)


__all__ = ["PatternVariantDestructureSkipNArgumentsAst"]
