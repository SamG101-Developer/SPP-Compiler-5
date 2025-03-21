from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class PatternVariantDestructureSkip1ArgumentAst(Asts.Ast, Asts.Mixins.AbstractPatternVariantAst):
    tok_underscore: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_underscore = self.tok_underscore or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkUnderscore)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_underscore.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_underscore.pos_end

    def convert_to_variable(self, **kwargs) -> Asts.LocalVariableDestructureSkip1ArgumentAst:
        # Convert the skip 1 argument destructuring into a local variable skip 1 argument destructuring.
        return Asts.LocalVariableDestructureSkip1ArgumentAst(self.pos, self.tok_underscore)


__all__ = [
    "PatternVariantDestructureSkip1ArgumentAst"]
