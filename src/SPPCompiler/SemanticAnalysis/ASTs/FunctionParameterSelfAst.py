from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Optional

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class FunctionParameterSelfAst(Ast, Ordered, VariableNameExtraction):
    tok_mut: Optional[Asts.TokenAst] = field(default=None)
    convention: Asts.ConventionAst = field(default_factory=lambda: Asts.ConventionMovAst())
    name: Asts.IdentifierAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    _arbitrary: bool = field(default=False)
    _true_self_type: Optional[Asts.TypeAst] = field(default=None)

    def __post_init__(self) -> None:
        assert self.name
        self._arbitrary = self.type is not None
        self.type = self.type or CommonTypes.Self(self.pos)
        self._variant = "Self"

    def __eq__(self, other: FunctionParameterSelfAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, FunctionParameterSelfAst)

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.convention.print(printer),
            self.name.print(printer),
            f": {self.type}" if self._arbitrary else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    @functools.cached_property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return Seq([self.name])

    @functools.cached_property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.name

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the type.
        self.type.analyse_semantics(scope_manager, **kwargs)

        # Check the "type" is either "Self" or superimposes "Deref[Self]". If not, raise an error.
        if self._arbitrary:

            # The convention is taken from the arbitrary type.
            self.convention = self.type.get_convention()

            deref_type = CommonTypes.DerefRef(self._true_self_type, pos=self.pos)
            deref_type.analyse_semantics(scope_manager, **kwargs)

            self_type_super_types = scope_manager.current_scope.get_symbol(self.type).scope.direct_sup_types
            if not self_type_super_types.any(lambda t: t.symbolic_eq(deref_type, scope_manager.current_scope, scope_manager.current_scope)):
                raise SemanticErrors.InvalidSelfTypeError().add(self.type).scopes(scope_manager.current_scope)

        # Create the variable using ASTs, because "let self: ..." will be a parse error.
        ast = Asts.LetStatementUninitializedAst(
            pos=self.pos,
            assign_to=Asts.LocalVariableSingleIdentifierAst(self.pos, self.tok_mut, self.name, None),
            type=self.type)
        ast.analyse_semantics(scope_manager, **kwargs)

        # Mark the symbol as initialized.
        symbol = scope_manager.current_scope.get_symbol(self.name)
        symbol.is_mutable = self.tok_mut is not None or isinstance(self.convention, Asts.ConventionMutAst)
        symbol.memory_info.ast_borrowed = self.convention if type(self.convention) is not Asts.ConventionMovAst else None
        symbol.memory_info.is_borrow_mut = isinstance(self.convention, Asts.ConventionMutAst)
        symbol.memory_info.is_borrow_ref = isinstance(self.convention, Asts.ConventionRefAst)
        symbol.memory_info.initialized_by(self)


__all__ = ["FunctionParameterSelfAst"]
