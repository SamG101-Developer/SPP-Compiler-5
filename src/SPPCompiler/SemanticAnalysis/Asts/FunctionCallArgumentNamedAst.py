from __future__ import annotations

from dataclasses import dataclass, field

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors


@dataclass
class FunctionCallArgumentNamedAst(Asts.Ast, Asts.Mixins.OrderableAst, Asts.Mixins.TypeInferrable):
    name: Asts.IdentifierAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default=None)
    convention: Asts.ConventionAst = field(default=None)
    value: Asts.ExpressionAst = field(default=None)
    _type_from_self: Asts.TypeAst = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.tok_assign = self.tok_assign or Asts.TokenAst.raw(pos=self.pos, token_type=SppTokenType.TkAssign)
        self.convention = self.convention or Asts.ConventionMovAst(pos=self.pos)
        self._variant = "Named"
        assert self.name is not None and self.value is not None

    def __eq__(self, other: FunctionCallArgumentNamedAst) -> bool:
        # Check both ASTs are the same type and have the same name and value.
        return isinstance(other, FunctionCallArgumentNamedAst) and self.name == other.name and self.value == other.value

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.name.print(printer),
            self.tok_assign.print(printer),
            self.convention.print(printer),
            self.value.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.value.pos_end

    def infer_type(self, sm: ScopeManager, **kwargs) -> Asts.TypeAst:
        if self._type_from_self:
            return self._type_from_self
        inferred_type = self.value.infer_type(sm, **kwargs)

        # The convention is either from the convention attribute or the symbol information.
        true_convention = inferred_type.get_convention() if isinstance(self.convention, Asts.ConventionMovAst) else self.convention
        return inferred_type.with_convention(true_convention)

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(
                self.value).scopes(sm.current_scope)

        # Analyse the value of the named argument.
        self.value.analyse_semantics(sm, **kwargs)


__all__ = [
    "FunctionCallArgumentNamedAst"]
