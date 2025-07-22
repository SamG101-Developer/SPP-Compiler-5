from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from SPPCompiler.SemanticAnalysis import Asts
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter, ast_printer_method
from SPPCompiler.SemanticAnalysis.Utils.CommonTypes import CommonTypes


@dataclass(slots=True, repr=False)
class FunctionParameterSelfAst(Asts.Ast, Asts.Mixins.OrderableAst, Asts.Mixins.VariableLikeAst):
    tok_mut: Optional[Asts.TokenAst] = field(default=None)
    convention: Optional[Asts.ConventionAst] = field(default=None)
    name: Asts.IdentifierAst = field(default=None)
    type: Asts.TypeAst = field(default=None)
    _true_self_type: Optional[Asts.TypeAst] = field(default=None)

    def __post_init__(self) -> None:
        self.type = CommonTypes.Self(self.pos)
        self._variant = "Self"

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.convention.print(printer) if self.convention else "",
            self.name.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.type.pos_end

    @property
    def extract_names(self) -> list[Asts.IdentifierAst]:
        return [self.name]

    @property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.name

    def analyse_semantics(self, sm: ScopeManager, **kwargs) -> None:
        # Analyse the type.
        self.type.analyse_semantics(sm, **kwargs)
        self.type = sm.current_scope.get_symbol(self.type).fq_name

        # Create the variable using ASTs, because "let self: ..." will be a parse error.
        ast = Asts.LetStatementUninitializedAst(
            pos=self.pos,
            assign_to=Asts.LocalVariableSingleIdentifierAst(self.pos, self.tok_mut, self.name, None),
            type=self.type.with_convention(self.convention))
        ast.analyse_semantics(sm, explicit_type=ast.type, **kwargs)

        # Mark the symbol as initialized. The "mut" being also set from the "&mut" is because "&mut self" implies symbol
        # mutability as-well.
        sym = sm.current_scope.get_symbol(self.name)
        sym.is_mutable = self.tok_mut is not None or type(self.convention) is Asts.ConventionMutAst
        sym.memory_info.initialized_by(self)
        sym.memory_info.ast_borrowed = self.convention
        sym.memory_info.is_borrow_mut = type(self.convention) is Asts.ConventionMutAst
        sym.memory_info.is_borrow_ref = type(self.convention) is Asts.ConventionRefAst

    def check_memory(self, sm: ScopeManager, **kwargs) -> None:
        sym = sm.current_scope.get_symbol(self.name)
        sym.memory_info.initialized_by(self)


__all__ = [
    "FunctionParameterSelfAst"]
