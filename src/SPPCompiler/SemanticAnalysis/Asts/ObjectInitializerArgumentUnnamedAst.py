from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class ObjectInitializerArgumentUnnamedAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    is_default: Optional[Asts.TokenAst] = field(default=None)
    name: Asts.IdentifierAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name is not None

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
        # Analyse the name of the argument.
        self.name.analyse_semantics(sm, **kwargs)


__all__ = [
    "ObjectInitializerArgumentUnnamedAst"]
