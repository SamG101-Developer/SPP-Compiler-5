from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import functools, os

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.ModuleImplementationAst import ModuleImplementationAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ModulePrototypeAst(Ast, CompilerStages):
    body: ModuleImplementationAst
    tok_eof: TokenAst

    _name: str = field(init=False, default="")

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.body.print(printer)

    @functools.cached_property
    def name(self) -> IdentifierAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst

        parts = self._name.split(os.path.sep)
        parts = parts[parts.index("src") + 1 :]
        name = "::".join(parts)
        return IdentifierAst(self.pos, name)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the module implementation.
        self.body.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ModulePrototypeAst"]
