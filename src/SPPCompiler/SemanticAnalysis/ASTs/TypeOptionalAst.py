from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class TypeOptionalAst(Ast):
    tok_qst: TokenAst
    type: TypeAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return f""

    def to_type(self) -> TypeAst:
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
        return CommonTypes.Opt(self.type, self.type.pos)


__all__ = ["TypeOptionalAst"]
