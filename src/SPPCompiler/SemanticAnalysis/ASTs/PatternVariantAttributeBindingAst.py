from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAttributeBindingAst import LocalVariableAttributeBindingAst
    from SPPCompiler.SemanticAnalysis.ASTs.PatternVariantAst import PatternVariantNestedForAttributeBindingAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class PatternVariantAttributeBindingAst(Ast, PatternMapping):
    name: IdentifierAst
    tok_assign: TokenAst
    value: PatternVariantNestedForAttributeBindingAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.value.print(printer)]
        return "".join(string)

    def convert_to_variable(self, **kwargs) -> LocalVariableAttributeBindingAst:
        # Convert the attribute binding into a local variable attribute binding.
        from SPPCompiler.SemanticAnalysis import LocalVariableAttributeBindingAst
        return LocalVariableAttributeBindingAst(self.pos, self.name, self.tok_assign, self.value.convert_to_variable(**kwargs))


__all__ = ["PatternVariantAttributeBindingAst"]
