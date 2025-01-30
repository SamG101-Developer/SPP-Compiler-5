from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class BooleanLiteralAst(Ast, TypeInferrable):
    value: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.KwFalse))

    @std.override_method
    def __eq__(self, other: BooleanLiteralAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return self.value == other.value

    @staticmethod
    def from_python_literal(pos: int, value: bool) -> BooleanLiteralAst:
        token = Asts.TokenAst.raw(pos=pos, token=SppTokenType.KwTrue if value else SppTokenType.KwFalse)
        return BooleanLiteralAst(pos, token)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    @std.override_method
    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredType:
        # Create the standard "std::Bool" type.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        bool_type = CommonTypes.Bool(self.pos)
        return InferredType.from_type(bool_type)


__all__ = ["BooleanLiteralAst"]
