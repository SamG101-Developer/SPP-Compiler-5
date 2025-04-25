from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass(slots=True)
class GenericTypeParameterVariadicAst(Asts.Ast, Asts.Mixins.OrderableAst):
    tok_variadic: Asts.TokenAst = field(default=None)
    name: Asts.TypeAst = field(default=None)
    constraints: Asts.GenericTypeParameterInlineConstraintsAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_variadic = self.tok_variadic or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkDoubleDot)
        self.constraints = self.constraints or Asts.GenericTypeParameterInlineConstraintsAst(pos=self.pos)
        self._variant = "Variadic"
        assert self.name is not None

    def __eq__(self, other: GenericTypeParameterVariadicAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericTypeParameterVariadicAst) and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_variadic.print(printer),
            self.name.print(printer),
            self.constraints.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.name.pos_end  # check this

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Create a type symbol for this type in the current scope (class / function).
        symbol = TypeSymbol(name=self.name.type_parts()[0], type=None, is_generic=True)
        sm.current_scope.add_symbol(symbol)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self.name.analyse_semantics(sm, **kwargs)
        self.constraints.analyse_semantics(sm, **kwargs)


__all__ = [
    "GenericTypeParameterVariadicAst"]
