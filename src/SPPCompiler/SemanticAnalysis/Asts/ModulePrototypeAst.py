from __future__ import annotations

import os
from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext


@dataclass
class ModulePrototypeAst(Asts.Ast):
    body: Asts.ModuleImplementationAst = field(default_factory=Asts.ModuleImplementationAst)
    _name: str = field(init=False, default="")

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.body.print(printer)

    @property
    def pos_end(self) -> int:
        return self.body.pos_end

    @property
    def name(self) -> Asts.IdentifierAst:
        parts = self._name.split(os.path.sep)
        parts = parts[parts.index("src") + 1:]
        name = "::".join(parts)
        return Asts.IdentifierAst(self.pos, name)

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the module implementation.
        super().pre_process(ctx)
        self.body.pre_process(ctx)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Generate the module symbol.
        super().generate_top_level_scopes(sm)
        self.body.generate_top_level_scopes(sm)

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Alias the types in the module implementation.
        self.body.generate_top_level_aliases(sm, **kwargs)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        # Load the super scopes.
        self.body.load_super_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Pre-analyse the module implementation.
        self.body.pre_analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the module implementation.
        self.body.analyse_semantics(sm, **kwargs)


__all__ = [
    "ModulePrototypeAst"]
