from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True)
class PatternVariantAttributeBindingAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    name: Asts.IdentifierAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    value: Asts.PatternVariantNestedForAttributeBindingAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableAttributeBindingAst:
        # Convert the attribute binding into a local variable attribute binding.
        inner_value = self.value.convert_to_variable(**kwargs)
        variable = Asts.LocalVariableAttributeBindingAst(self.pos, self.name, self.tok_assign, inner_value)
        variable._from_pattern = True
        return variable


__all__ = [
    "PatternVariantAttributeBindingAst"]
