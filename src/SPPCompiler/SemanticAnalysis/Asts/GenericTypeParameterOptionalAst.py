from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter


@dataclass
class GenericTypeParameterOptionalAst(Asts.Ast, Asts.Mixins.OrderableAst):
    name: Asts.TypeAst = field(default=None)
    constraints: Asts.GenericTypeParameterInlineConstraintsAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    default: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        self.constraints = self.constraints or Asts.GenericTypeParameterInlineConstraintsAst()
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        assert self.name is not None and self.default is not None
        self._variant = "Optional"

    def __eq__(self, other: GenericTypeParameterOptionalAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericTypeParameterOptionalAst) and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.constraints.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.default.pos_end

    def generate_top_level_scopes(self, sm: ScopeManager) -> None:
        # Create a type symbol for this type in the current scope (class / function).
        symbol = TypeSymbol(name=self.name.type_parts()[0], type=None, is_generic=True)
        sm.current_scope.add_symbol(symbol)

    def qualify_types(self, sm: ScopeManager, **kwargs) -> None:
        # Qualify the default value type.
        self.default.analyse_semantics(sm, **kwargs)
        self.default = sm.current_scope.get_symbol(self.default).fq_name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        self.name.analyse_semantics(sm, **kwargs)
        self.constraints.analyse_semantics(sm, **kwargs)


__all__ = [
    "GenericTypeParameterOptionalAst"]
