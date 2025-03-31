from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class PatternVariantSingleIdentifierAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    tok_mut: Optional[Asts.TokenAst] = field(default=None)
    name: Asts.IdentifierAst = field(default=None)
    alias: Optional[Asts.LocalVariableSingleIdentifierAliasAst] = field(default=None)

    def __post_init__(self) -> None:
        assert self.name is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) if self.tok_mut is not None else "",
            self.name.print(printer),
            (" " + self.alias.print(printer)) if self.alias is not None else ""]
        return " ".join(string)

    @property
    def pos_end(self) -> int:
        return self.alias.pos_end if self.alias else self.name.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableSingleIdentifierAst:
        # Convert the single identifier into a local variable single identifier.
        variable = Asts.LocalVariableSingleIdentifierAst(self.pos, self.tok_mut, self.name, self.alias)
        variable._from_pattern = True
        return variable

    def analyse_semantics(self, sm: ScopeManager, condition: Asts.ExpressionAst = None, **kwargs) -> None:
        # Create the new variable from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        new_ast = Asts.LetStatementInitializedAst(pos=variable.pos, assign_to=variable, value=condition)
        new_ast.analyse_semantics(sm, **kwargs)


__all__ = [
    "PatternVariantSingleIdentifierAst"]
