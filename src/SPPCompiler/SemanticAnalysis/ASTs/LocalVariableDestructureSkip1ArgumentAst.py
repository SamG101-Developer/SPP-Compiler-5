from __future__ import annotations

import functools
from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class LocalVariableDestructureSkip1ArgumentAst(Ast, VariableNameExtraction):
    tok_underscore: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkUnderscore))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.tok_underscore.print(printer)

    @property
    def pos_end(self) -> int:
        return self.tok_underscore.pos_end

    @functools.cached_property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return Seq()


__all__ = ["LocalVariableDestructureSkip1ArgumentAst"]
