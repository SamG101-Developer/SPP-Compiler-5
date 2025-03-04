from __future__ import annotations

from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import TypeInferrable, InferredTypeInfo
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionCallArgumentNamedAst(Ast, Ordered, TypeInferrable):
    name: Asts.IdentifierAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAssign))
    convention: Asts.ConventionAst = field(default_factory=Asts.ConventionMovAst)
    value: Asts.ExpressionAst = field(default=None)
    _type_from_self: Asts.TypeAst = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        assert self.name
        assert self.value
        self._variant = "Named"

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

    def infer_type(self, scope_manager: ScopeManager, **kwargs) -> InferredTypeInfo:
        if self._type_from_self:
            return InferredTypeInfo(self._type_from_self, self.convention)
        inferred_type = self.value.infer_type(scope_manager, **kwargs)

        # The convention is either from the convention attribute or the symbol information.
        convention = inferred_type.convention if isinstance(self.convention, Asts.ConventionMovAst) else self.convention
        return InferredTypeInfo(inferred_type.type, self.convention)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the value.
        if isinstance(self.value, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.value)

        # Analyse the value of the named argument.
        self.value.analyse_semantics(scope_manager, **kwargs)


__all__ = ["FunctionCallArgumentNamedAst"]
