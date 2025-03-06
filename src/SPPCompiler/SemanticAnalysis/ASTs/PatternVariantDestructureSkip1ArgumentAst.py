from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.PatternMapping import PatternMapping


@dataclass
class PatternVariantDestructureSkip1ArgumentAst(Ast, PatternMapping):
    tok_underscore: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkUnderscore))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_underscore.print(printer)

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableDestructureSkip1ArgumentAst:
        # Convert the skip 1 argument destructuring into a local variable skip 1 argument destructuring.
        return Asts.LocalVariableDestructureSkip1ArgumentAst(self.pos, self.tok_underscore)


__all__ = ["PatternVariantDestructureSkip1ArgumentAst"]
