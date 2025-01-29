from __future__ import annotations

from dataclasses import dataclass
from typing import Self

import std

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class ConventionMovAst(Ast):
    @std.override_method
    def __eq__(self, other: ConventionMovAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, ConventionMovAst)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return ""


__all__ = ["ConventionMovAst"]
