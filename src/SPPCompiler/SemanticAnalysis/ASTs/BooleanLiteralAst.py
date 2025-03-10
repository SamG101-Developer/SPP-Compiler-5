from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class BooleanLiteralAst(Ast, TypeInferrable):
    value: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.KwFalse))

    def __eq__(self, other: BooleanLiteralAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return self.value == other.value

    @staticmethod
    def from_python_literal(pos: int, value: bool) -> BooleanLiteralAst:
        token = Asts.TokenAst.raw(pos=pos, token_type=SppTokenType.KwTrue if value else SppTokenType.KwFalse)
        return BooleanLiteralAst(pos, token)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Create the standard "std::Bool" type.
        return CommonTypes.Bool(self.pos)


__all__ = ["BooleanLiteralAst"]
