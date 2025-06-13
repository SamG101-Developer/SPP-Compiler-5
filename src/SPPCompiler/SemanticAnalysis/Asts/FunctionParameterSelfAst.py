from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.AstUtils.AstTypeUtils import AstTypeUtils
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Utils.SemanticError import SemanticErrors
from SPPCompiler.Utils.Sequence import Seq


@dataclass(slots=True)
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

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.convention.print(printer) if self.convention else "",
            self.name.print(printer),
            self.type.print(printer) if self._arbitrary else ""]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    @property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return [self.name]

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the type.
        self.type.analyse_semantics(sm, **kwargs)

        # Check the "type" is either "Self" or superimposes "Deref[Self]". If not, raise an error.
        if self._arbitrary:

            # The convention is taken from the arbitrary type.
            self.convention = self.type.convention

            deref_type = CommonTypes.DerefRef(self.pos, self._true_self_type)
            deref_type.analyse_semantics(sm, **kwargs)

            self_type_super_types = sm.current_scope.get_symbol(self.type).scope.direct_sup_types
            if not any(AstTypeUtils.symbolic_eq(t, deref_type, sm.current_scope, sm.current_scope) for t in self_type_super_types):
                raise SemanticErrors.InvalidSelfTypeError().add(
                    self.type).scopes(sm.current_scope)

        # Create the variable using ASTs, because "let self: ..." will be a parse error.
        ast = Asts.LetStatementUninitializedAst(
            pos=self.pos,
            assign_to=Asts.LocalVariableSingleIdentifierAst(self.pos, self.tok_mut, self.name, None),
            type=self.type)
        ast.analyse_semantics(sm, **kwargs)

        # Mark the symbol as initialized. The "mut" being also set from the "&mut" is because "&mut self" implies symbol
        # mutability as-well.
        sym = sm.current_scope.get_symbol(self.name)
        sym.is_mutable = self.tok_mut is not None or isinstance(self.convention, Asts.ConventionMutAst)
        sym.memory_info.initialized_by(self)
        sym.memory_info.ast_borrowed = self.convention
        sym.memory_info.is_borrow_mut = isinstance(self.convention, Asts.ConventionMutAst)
        sym.memory_info.is_borrow_ref = isinstance(self.convention, Asts.ConventionRefAst)

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        sym = sm.current_scope.get_symbol(self.name)
        sym.memory_info.initialized_by(self)


__all__ = [
    "FunctionParameterSelfAst"]
