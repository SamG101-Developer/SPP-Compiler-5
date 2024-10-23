from __future__ import annotations
from dataclasses import dataclass

from SPPCompiler.LexicalAnalysis.Token import Token
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import *
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class Ast:
    pos: int
    
    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = ""
        for attribute in self.__dict__.values():
            if isinstance(attribute, Ast):
                string += f"{attribute.print(printer)} "
            elif isinstance(attribute, Seq):
                string += f"{attribute.print(printer)}"
            elif isinstance(attribute, str):
                string += f"{attribute}"
            elif isinstance(attribute, Token):
                string += attribute.token_metadata
        return string
    
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
