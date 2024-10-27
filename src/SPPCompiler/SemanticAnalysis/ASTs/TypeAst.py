from __future__ import annotations
from convert_case import pascal_case
from dataclasses import dataclass
from typing import TYPE_CHECKING
import hashlib

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypePartAst import TypePartAst
    from SPPCompiler.SemanticAnalysis.Scoping.Scope import Scope


@dataclass
class TypeAst(Ast, Stage4_SemanticAnalyser):
    namespace: Seq[IdentifierAst]
    types: Seq[TypePartAst]

    def __post_init__(self) -> None:
        # Convert the namespace and types into a sequence.
        self.namespace = Seq(self.namespace)
        self.types = Seq(self.types)

    def __eq__(self, other: TypeAst) -> bool:
        # Check both ASTs are the same type and have the same namespace and types.
        return isinstance(other, TypeAst) and self.namespace == other.namespace and self.types == other.types

    def __hash__(self) -> int:
        # Hash the namespace and types into a fixed string and convert it into an integer.
        return int.from_bytes(hashlib.md5("".join([str(p) for p in self.namespace + self.types]).encode()).digest())

    def __json__(self) -> str:
        return f"cls {self.print(AstPrinter())}"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.namespace.print(printer, "::") + "::" if self.namespace else "",
            self.types.print(printer, "::")]
        return "".join(string)

    @staticmethod
    def from_identifier(identifier: IdentifierAst) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst, TypeAst
        return TypeAst(identifier.pos, Seq(), Seq([GenericIdentifierAst.from_identifier(identifier)]))

    @staticmethod
    def from_function_identifier(identifier: IdentifierAst) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import IdentifierAst
        mock_type_name = IdentifierAst(identifier.pos, f"${pascal_case(identifier.value.replace("_", " "))}")
        return TypeAst.from_identifier(mock_type_name)

    def without_generics(self) -> TypeAst:
        from SPPCompiler.SemanticAnalysis import GenericIdentifierAst
        match self.types[-1]:
            case GenericIdentifierAst(): return TypeAst(self.pos, self.namespace, self.types[:-1] + [self.types[-1].without_generics()])
            case _: return TypeAst(self.pos, self.namespace.copy(), self.types.copy())

    def symbolic_eq(self, that: TypeAst, self_scope: Scope, that_scope: Scope) -> bool:
        ...

    def analyse_semantics(self, scope_handler: ScopeManager, **kwargs) -> None:
        ...


__all__ = ["TypeAst"]
