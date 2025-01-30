from __future__ import annotations

from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class ObjectInitializerArgumentUnnamedAst(Ast, TypeInferrable):
    is_default: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkDblDot))
    name: Asts.IdentifierAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.name.print(printer)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Infer the type of the argument.
        return self.name.infer_type(scope_manager, **kwargs)

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the name of the argument.
        self.name.analyse_semantics(scope_manager, **kwargs)


__all__ = ["ObjectInitializerArgumentUnnamedAst"]
