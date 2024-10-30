from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableDestructureSkip1ArgumentAst import LocalVariableDestructureSkip1ArgumentAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst


@dataclass
class PatternVariantDestructureSkip1ArgumentAst(Ast, PatternMapping):
    tok_underscore: TokenAst

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_underscore.print(printer)

    def convert_to_variable(self, **kwargs) -> LocalVariableDestructureSkip1ArgumentAst:
        # Convert the skip 1 argument destructuring into a local variable skip 1 argument destructuring.
        return LocalVariableDestructureSkip1ArgumentAst(self.pos, self.tok_underscore)


__all__ = ["PatternVariantDestructureSkip1ArgumentAst"]
