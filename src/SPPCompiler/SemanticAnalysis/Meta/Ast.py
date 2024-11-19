from __future__ import annotations
from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import *


@dataclass
class Ast:
    pos: int

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        ...

    def __eq__(self, other: Ast) -> bool:
        return isinstance(other, Ast)

    def __str__(self) -> str:
        printer = AstPrinter()
        return self.print(printer)


class Default:
    @staticmethod
    def default() -> Default:
        ...


__all__ = ["Ast", "Default"]
