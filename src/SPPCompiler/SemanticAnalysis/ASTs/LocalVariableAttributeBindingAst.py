from __future__ import annotations

import functools
import std
from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class LocalVariableAttributeBindingAst(Ast, VariableNameExtraction):
    name: Asts.IdentifierAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkAssign))
    value: Asts.LocalVariableNestedForAttributeBindingAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        assert self.value

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.value.print(printer)]
        return "".join(string)

    @functools.cached_property
    @std.override_method
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.value.extract_names


__all__ = ["LocalVariableAttributeBindingAst"]
