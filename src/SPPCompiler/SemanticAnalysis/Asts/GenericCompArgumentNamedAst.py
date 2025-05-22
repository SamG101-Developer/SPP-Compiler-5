from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy


@dataclass(slots=True)
class GenericCompArgumentNamedAst(Asts.Ast, Asts.Mixins.OrderableAst):
    name: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        self.value = self.value or Asts.IdentifierAst.from_type(self.name)
        self._variant = "Named"

    def __eq__(self, other: GenericCompArgumentNamedAst) -> bool:
        return isinstance(other, GenericCompArgumentNamedAst) and self.name == other.name and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.name)

    def __deepcopy__(self, memodict=None) -> GenericCompArgumentNamedAst:
        # Create a deep copy of the AST.
        return GenericCompArgumentNamedAst(
            pos=self.pos, name=self.name, tok_assign=self.tok_assign, value=fast_deepcopy(self.value))

    def __str__(self) -> str:
        string = [
            str(self.name),
            str(self.tok_assign),
            str(self.value)]
        return "".join(string)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.value.print(printer)]  # todo ?
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos

    @staticmethod
    def from_symbol(symbol: VariableSymbol) -> GenericCompArgumentNamedAst:
        return GenericCompArgumentNamedAst(
            name=Asts.TypeSingleAst.from_identifier(symbol.name),
            value=symbol.memory_info.ast_comptime_const)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.value).scopes(sm.current_scope)

        # Analyse the value of the named argument.
        self.value.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        """
        Check the memory integrity of the value. Comptime constants don't have nested checks as they are a subset of
        possible expressions, and none of these values have deeper ASTs that would require extra analysis.

        :param sm: The scope manager.
        :param kwargs: Additional keyword arguments.
        """

        AstMemoryUtils.enforce_memory_integrity(
            self.value, self.value, sm, check_move=True, check_partial_move=True, check_move_from_borrowed_ctx=True,
            check_pins=True, mark_moves=True)


__all__ = [
    "GenericCompArgumentNamedAst"]
