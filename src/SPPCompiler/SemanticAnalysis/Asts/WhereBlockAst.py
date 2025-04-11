from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class WhereBlockAst(Asts.Ast):
    kw_where: Asts.TokenAst = field(default=None)
    constraint_group: Asts.WhereConstraintsGroupAst = field(default=None)

    def __post_init__(self) -> None:
        self.kw_where = self.kw_where or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.KwWhere)
        self.constraint_group = self.constraint_group or Asts.WhereConstraintsGroupAst(pos=self.pos)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        if self.constraint_group.type_constraints_pairs:
            string = [
                self.kw_where.print(printer) + " ",
                self.constraint_group.print(printer)]
        else:
            string = []
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.constraint_group.pos_end


__all__ = [
    "WhereBlockAst"]
