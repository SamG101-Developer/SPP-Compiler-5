from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class LocalVariableDestructureSkipNArgumentsAst(Ast, VariableNameExtraction):
    tok_variadic: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkDoubleDot))
    binding: Optional[Asts.LocalVariableSingleIdentifierAst] = field(default=None)

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

    @functools.cached_property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.binding.extract_names if self.binding else Seq()


__all__ = ["LocalVariableDestructureSkipNArgumentsAst"]
