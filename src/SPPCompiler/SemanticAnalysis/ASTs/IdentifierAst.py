from __future__ import annotations
from dataclasses import dataclass
import hashlib

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class IdentifierAst(Ast):
    value: str

    def __eq__(self, other: IdentifierAst) -> bool:
        return isinstance(other, IdentifierAst) and self.value == other.value

    def __hash__(self):
        return int.from_bytes(hashlib.md5(self.value.encode()).digest())

    def __json__(self) -> str:
        return self.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        return self.value


__all__ = ["IdentifierAst"]
