from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy


@dataclass(slots=True)
class GenericTypeArgumentNamedAst(Asts.Ast, Asts.Mixins.OrderableAst):
    name: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    value: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        self._variant = "Named"
        self.value = self.value or self.name

    def __eq__(self, other: GenericTypeArgumentNamedAst) -> bool:
        return other.__class__ is GenericTypeArgumentNamedAst and self.name == other.name and self.value == other.value

    def __deepcopy__(self, memodict=None) -> GenericTypeArgumentNamedAst:
        # Create a deep copy of the AST.
        return GenericTypeArgumentNamedAst(
            pos=self.pos,
            name=self.name,
            tok_assign=self.tok_assign,
            value=fast_deepcopy(self.value))

    def __str__(self) -> str:
        string = [str(self.name), str(self.tok_assign), str(self.value)]
        return "".join(string)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = [self.name.print(printer), self.tok_assign.print(printer), self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos

    @staticmethod
    def from_symbol(symbol: TypeSymbol) -> GenericTypeArgumentNamedAst:
        value = symbol.scope.type_symbol.fq_name.with_convention(symbol.convention) if symbol.scope else symbol.scope
        return GenericTypeArgumentNamedAst(name=Asts.TypeSingleAst.from_generic_identifier(symbol.name), value=value)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the name and value of the generic type argument.
        convention = self.value.get_convention()
        self.value.analyse_semantics(sm, **kwargs)
        self.value = sm.current_scope.get_symbol(self.value).fq_name.with_convention(convention)


__all__ = [
    "GenericTypeArgumentNamedAst"]
