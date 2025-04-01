from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class FunctionParameterSelfAst(Asts.Ast, Asts.Mixins.OrderableAst, Asts.Mixins.VariableLikeAst):
    tok_mut: Optional[Asts.TokenAst] = field(default=None)
    convention: Optional[Asts.ConventionAst] = field(default=None)
    name: Asts.IdentifierAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    _arbitrary: bool = field(default=False)
    _true_self_type: Optional[Asts.TypeAst] = field(default=None)

    def __post_init__(self) -> None:
        self._arbitrary = self.type is not None
        self.type = self.type or CommonTypes.Self(self.pos)
        self._variant = "Self"
        assert self.name is not None

    def __eq__(self, other: FunctionParameterSelfAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, FunctionParameterSelfAst)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.convention.print(printer) if self.convention else "",
            self.name.print(printer),
            f": {self.type}" if self._arbitrary else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return Seq([self.name])

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the type.
        self.type.analyse_semantics(sm, **kwargs)

        # Check the "type" is either "Self" or superimposes "Deref[Self]". If not, raise an error.
        if self._arbitrary:

            # The convention is taken from the arbitrary type.
            self.convention = self.type.get_conventions()[0] if self.type.get_conventions() else None

            deref_type = CommonTypes.DerefRef(self.pos, self._true_self_type)
            deref_type.analyse_semantics(sm, **kwargs)

            self_type_super_types = sm.current_scope.get_symbol(self.type).scope.direct_sup_types
            if not self_type_super_types.any(lambda t: t.symbolic_eq(deref_type, sm.current_scope, sm.current_scope)):
                raise SemanticErrors.InvalidSelfTypeError().add(
                    self.type).scopes(sm.current_scope)

        # Create the variable using ASTs, because "let self: ..." will be a parse error.
        ast = Asts.LetStatementUninitializedAst(
            pos=self.pos,
            assign_to=Asts.LocalVariableSingleIdentifierAst(self.pos, self.tok_mut, self.name, None),
            type=self.type)
        ast.analyse_semantics(sm, **kwargs)

        # Mark the symbol as initialized.
        symbol = sm.current_scope.get_symbol(self.name)
        symbol.is_mutable = self.tok_mut is not None or isinstance(self.convention, Asts.ConventionMutAst)
        symbol.memory_info.ast_borrowed = self.convention
        symbol.memory_info.is_borrow_mut = isinstance(self.convention, Asts.ConventionMutAst)
        symbol.memory_info.is_borrow_ref = isinstance(self.convention, Asts.ConventionRefAst)
        symbol.memory_info.initialized_by(self)


__all__ = [
    "FunctionParameterSelfAst"]
