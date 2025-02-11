from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class PatternVariantSingleIdentifierAst(Ast, PatternMapping):
    tok_mut: Optional[Asts.TokenAst] = field(default=None)
    name: Asts.IdentifierAst = field(default=None)
    alias: Optional[Asts.LocalVariableSingleIdentifierAliasAst] = field(default=None)

    def __post_init__(self) -> None:
        assert self.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) if self.tok_mut is not None else "",
            self.name.print(printer),
            (" " + self.alias.print(printer)) if self.alias is not None else ""]
        return " ".join(string)

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableSingleIdentifierAst:
        # Convert the single identifier into a local variable single identifier.
        from SPPCompiler.SemanticAnalysis import LocalVariableSingleIdentifierAst
        return LocalVariableSingleIdentifierAst(self.pos, self.tok_mut, self.name, self.alias)

    def analyse_semantics(self, scope_manager: ScopeManager, condition: Asts.ExpressionAst = None, **kwargs) -> None:
        # Create the new variable from the pattern in the patterns scope.
        variable = self.convert_to_variable(**kwargs)
        new_ast = Asts.LetStatementInitializedAst(pos=variable.pos, assign_to=variable, value=condition)
        new_ast.analyse_semantics(scope_manager, **kwargs)


__all__ = ["PatternVariantSingleIdentifierAst"]
