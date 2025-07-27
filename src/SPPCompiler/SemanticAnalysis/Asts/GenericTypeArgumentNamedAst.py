from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy


@dataclass(slots=True, repr=False)
class GenericTypeArgumentNamedAst(Asts.Ast, Asts.Mixins.OrderableAst):
    name: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    value: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self._variant = "Named"
        self.value = self.value or self.name

    def __eq__(self, other: GenericTypeArgumentNamedAst) -> bool:
        return type(other) is GenericTypeArgumentNamedAst and self.value == other.value  # and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __deepcopy__(self, memodict=None) -> GenericTypeArgumentNamedAst:
        # Create a deep copy of the AST.
        return GenericTypeArgumentNamedAst(
            pos=self.pos,
            name=self.name,
            tok_assign=self.tok_assign,
            value=fast_deepcopy(self.value))

    def __str__(self) -> str:
        string = [str(self.name), "=", str(self.value)]
        return "".join(string)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        string = [self.name.print(printer), "=", self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos

    @staticmethod
    def from_symbol(symbol: TypeSymbol) -> GenericTypeArgumentNamedAst:
        value = symbol.scope.type_symbol.fq_name.with_convention(symbol.convention) if symbol.scope else symbol.scope
        return GenericTypeArgumentNamedAst(name=fast_deepcopy(symbol.name), value=value)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the name and value of the generic type argument.
        convention = self.value.convention
        self.value.analyse_semantics(sm, **kwargs)
        self.value = sm.current_scope.get_symbol(self.value).fq_name.with_convention(convention)


__all__ = [
    "GenericTypeArgumentNamedAst"]
