from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstMemoryUtils import AstMemoryUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.FastDeepcopy import fast_deepcopy


@dataclass(slots=True)
class GenericCompArgumentUnnamedAst(Asts.Ast, Asts.Mixins.OrderableAst):
    value: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        # assert self.value
        self._variant = "Unnamed"

    def __eq__(self, other: GenericCompArgumentUnnamedAst) -> bool:
        # Check both ASTs are the same type and have the same value.
        return isinstance(other, GenericCompArgumentUnnamedAst) and self.value == other.value

    def __deepcopy__(self, memodict=None) -> GenericCompArgumentUnnamedAst:
        # Create a deep copy of the AST.
        return GenericCompArgumentUnnamedAst(
            pos=self.pos,
            value=fast_deepcopy(self.value))

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        return self.value.print(printer)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.value).scopes(sm.current_scope)

        # Analyse the value of the unnamed argument.
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
    "GenericCompArgumentUnnamedAst"]
