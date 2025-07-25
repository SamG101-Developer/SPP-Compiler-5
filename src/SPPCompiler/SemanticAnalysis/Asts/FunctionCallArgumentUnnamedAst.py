from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass(slots=True, repr=False)
class FunctionCallArgumentUnnamedAst(Asts.Ast, Asts.Mixins.OrderableAst, Asts.Mixins.TypeInferrable):
    convention: Asts.ConventionAst = field(default=None)
    tok_unpack: Optional[Asts.TokenAst] = field(default=None)
    value: Asts.ExpressionAst = field(default=None)
    _type_from_self: Asts.TypeAst = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._variant = "Unnamed"

    def __hash__(self) -> int:
        # Get the id of the AST (same as "is" matching).
        return id(self)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.convention.print(printer) if self.convention else "",
            self.tok_unpack.print(printer) if self.tok_unpack is not None else "",
            self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        if self._type_from_self:
            return self._type_from_self

        # Attach the convention to the inferred type.
        return self.value.infer_type(sm, **kwargs).with_convention(self.convention)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.value).scopes(sm.current_scope)

        # Analyse the semantics of the argument's value.
        self.value.analyse_semantics(sm, **kwargs)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        self.value.check_memory(sm, **kwargs)


__all__ = [
    "FunctionCallArgumentUnnamedAst"]
