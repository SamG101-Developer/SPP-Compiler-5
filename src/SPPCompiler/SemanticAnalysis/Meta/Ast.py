from __future__ import annotations
from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import *
import std


@dataclass
class Ast(std.BaseObject):
    pos: int = field(default=-1)

    @ast_printer_method
    @std.abstract_method
    def print(self, printer: AstPrinter) -> str:
        ...

    @std.virtual_method
    def __eq__(self, other: Ast) -> bool:
        return isinstance(other, Ast)

    def __str__(self) -> str:
        printer = AstPrinter()
        return self.print(printer)


__all__ = ["Ast"]
