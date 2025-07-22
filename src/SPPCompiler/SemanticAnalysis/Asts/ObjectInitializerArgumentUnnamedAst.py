from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class ObjectInitializerArgumentUnnamedAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    is_default: Optional[Asts.TokenAst] = field(default=None)
    name: Asts.ExpressionAst = field(default=None)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.name.print(printer)

    @property
    def pos_end(self) -> int:
        return self.name.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Infer the type of the argument.
        return self.name.infer_type(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Check the argument is an identifier (not done in parser so error occurs here)
        if type(self.name) is not Asts.IdentifierAst:
            raise SemanticErrors.InvalidObjectInitializerArgumentError().add(self.name).scopes(sm.current_scope)

        # Analyse the name of the argument.
        self.name.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Check the memory of the argument.
        self.name.check_memory(sm, **kwargs)


__all__ = [
    "ObjectInitializerArgumentUnnamedAst"]
