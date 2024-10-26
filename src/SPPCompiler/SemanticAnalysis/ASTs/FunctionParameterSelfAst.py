from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst


@dataclass
class FunctionParameterSelfAst(Ast):
    tok_mut: Optional[TokenAst]
    convention: ConventionAst
    name: IdentifierAst
    type: TypeAst = field(default=None, init=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes

        # Create defaults.
        self.type = CommonTypes.Self(self.pos)

    def __eq__(self, other: FunctionParameterSelfAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, FunctionParameterSelfAst)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.convention.print(printer),
            self.name.print(printer)]
        return "".join(string)


__all__ = ["FunctionParameterSelfAst"]
