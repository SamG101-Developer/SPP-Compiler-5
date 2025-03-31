from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class PatternVariantLiteralAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    literal: Asts.LiteralAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.literal is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.literal.print(printer)

    @property
    def pos_end(self) -> int:
        return self.literal.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableSingleIdentifierAst:
        # Convert the dummy single identifier into a local variable single identifier.
        variable = Asts.LocalVariableSingleIdentifierAst(pos=self.pos, name=Asts.IdentifierAst(self.pos, f"$l{id(self)}"))
        variable._from_pattern = True
        return variable

    def analyse_semantics(self, sm: ScopeManager, cond: Asts.ExpressionAst = None, **kwargs) -> None:
        # Analyse the literal.
        self.literal.analyse_semantics(sm, **kwargs)


__all__ = [
    "PatternVariantLiteralAst"]
