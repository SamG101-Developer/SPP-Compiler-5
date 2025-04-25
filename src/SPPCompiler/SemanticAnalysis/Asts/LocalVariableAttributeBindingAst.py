from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
class LocalVariableAttributeBindingAst(Asts.Ast, Asts.Mixins.VariableLikeAst):
    name: Asts.IdentifierAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    value: Asts.LocalVariableNestedForAttributeBindingAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        assert self.name is not None and self.value is not None

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.value.extract_names

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.value.extract_name


__all__ = [
    "LocalVariableAttributeBindingAst"]
