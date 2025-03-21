from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class LocalVariableDestructureSkip1ArgumentAst(Asts.Ast, Asts.Mixins.VariableLikeAst):
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

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return Seq()

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return Asts.IdentifierAst(self.pos, Asts.Mixins.VariableLikeAst.UNMATCHABLE_VARIABLE)


__all__ = [
    "LocalVariableDestructureSkip1ArgumentAst"]
