from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from llvmlite import ir

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CompilerStages import PreProcessingContext


@dataclass(slots=True)
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

        if "src" in parts:
            parts = parts[parts.index("src") + 1:]
            name = "::".join(parts)
        else:
            parts = [parts[0], parts[1] + ".spp"]
            name = "::".join(parts)

        return Asts.IdentifierAst(self.pos, name)

    def pre_process(self, ctx: PreProcessingContext) -> None:
        # Pre-process the module implementation.
        Asts.Ast.pre_process(self, ctx)
        self.body.pre_process(ctx)

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Generate the module symbol.
        Asts.Ast.generate_top_level_scopes(self, sm)
        self.body.generate_top_level_scopes(sm)

    def generate_top_level_aliases(self, sm: ScopeManager, **kwargs) -> None:
        # Alias the types in the module implementation.
        self.body.generate_top_level_aliases(sm, **kwargs)

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        # Qualify the types in the module implementation.
        self.body.qualify_types(sm, **kwargs)

    def load_super_scopes(self, sm: ScopeManager, **kwargs) -> None:
        # Load the super scopes.
        self.body.load_super_scopes(sm, **kwargs)

    def pre_analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Pre-analyse the module implementation.
        self.body.pre_analyse_semantics(sm, **kwargs)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the module implementation.
        self.body.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        # Check the memory of the module implementation.
        self.body.check_memory(sm, **kwargs)

    def code_gen(self, sm: ScopeManager, llvm_module: Optional[ir.Module] = None, **kwargs) -> ir.Module:
        # Generate the LLVM code for the module implementation.
        llvm_module = ir.Module(self.name)
        self.body.code_gen(sm, llvm_module, **kwargs)
        return llvm_module


__all__ = [
    "ModulePrototypeAst"]
