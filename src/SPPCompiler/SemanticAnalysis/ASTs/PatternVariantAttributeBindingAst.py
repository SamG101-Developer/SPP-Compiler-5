from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping


@dataclass
class PatternVariantAttributeBindingAst(Ast, PatternMapping):
    name: Asts.IdentifierAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkAssign))
    value: Asts.PatternVariantNestedForAttributeBindingAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        assert self.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.value.print(printer)]
        return "".join(string)

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableAttributeBindingAst:
        # Convert the attribute binding into a local variable attribute binding.
        return Asts.LocalVariableAttributeBindingAst(self.pos, self.name, self.tok_assign, self.value.convert_to_variable(**kwargs))


__all__ = ["PatternVariantAttributeBindingAst"]
