from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import *


@dataclass
class Ast(ABC):
    pos: int

    @ast_printer_method
    @abstractmethod
    def print(self, printer: AstPrinter) -> str:
        ...

    def __eq__(self, other: Ast) -> bool:
        return isinstance(other, Ast)

    def __str__(self) -> str:
        printer = AstPrinter()
        return self.print(printer)


class Default:
    @staticmethod
    @abstractmethod
    def default() -> Default:
        ...


__all__ = ["Ast", "Default"]
