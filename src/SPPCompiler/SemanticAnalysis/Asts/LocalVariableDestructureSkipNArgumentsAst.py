from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class LocalVariableDestructureSkipNArgumentsAst(Asts.Ast, Asts.Mixins.VariableLikeAst):
    tok_variadic: Asts.TokenAst = field(default=None)
    binding: Optional[Asts.LocalVariableSingleIdentifierAst] = field(default=None)

    def __post_init__(self) -> None:
        self.tok_variadic = self.tok_variadic or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDoubleDot)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_variadic.print(printer),
            self.binding.print(printer) if self.binding is not None else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.binding.pos_end if self.binding else self.tok_variadic.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.binding.extract_names if self.binding else Seq()

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return Asts.IdentifierAst(self.pos, Asts.Mixins.VariableLikeAst.UNMATCHABLE_VARIABLE)


__all__ = [
    "LocalVariableDestructureSkipNArgumentsAst"]
