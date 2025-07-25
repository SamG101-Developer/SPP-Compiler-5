from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes


@dataclass(slots=True, repr=False)
class StringLiteralAst(Asts.Ast, Asts.Mixins.TypeInferrable):
    value: Asts.TokenAst = field(default=None)

    def __post_init__(self) -> None:
        self.value = self.value or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.LxString)

    def __eq__(self, other: StringLiteralAst) -> bool:
        # Needed for cmp-generic arg checking
        return self.value.token_data == other.value.token_data

    def __hash__(self) -> int:
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        # Create the standard "std::string::Str" type.
        return CommonTypes.Str(self.pos)


__all__ = [
    "StringLiteralAst"]
