from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import functools, std

from SPPCompiler.SemanticAnalysis.Lang.CommonTypes import CommonTypes
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionParameterSelfAst(Ast, Ordered, VariableNameExtraction, CompilerStages):
    tok_mut: Optional[Asts.TokenAst] = field(default=None)
    convention: Asts.ConventionAst = field(default_factory=lambda: Asts.ConventionMovAst())
    name: Asts.IdentifierAst = field(default=None)
    type: Asts.TypeAst = field(default=None, init=False)

    def __post_init__(self) -> None:
        assert self.name
        self.type = CommonTypes.Self(self.pos)
        self._variant = "Self"

    @std.override_method
    def __eq__(self, other: FunctionParameterSelfAst) -> bool:
        # Check both ASTs are the same type.
        return isinstance(other, FunctionParameterSelfAst)

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_mut.print(printer) + " " if self.tok_mut else "",
            self.convention.print(printer),
            self.name.print(printer)]
        return "".join(string)

    @functools.cached_property
    @std.override_method
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return Seq([self.name])

    @functools.cached_property
    @std.override_method
    def extract_name(self) -> Asts.IdentifierAst:
        return self.name

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the type.
        self.type.analyse_semantics(scope_manager, **kwargs)

        # Create the variable using ASTs, because "let self: ..." will be a parse error.
        ast = Asts.LetStatementUninitializedAst(
            pos=self.pos,
            assign_to=Asts.LocalVariableSingleIdentifierAst(self.pos, self.tok_mut, self.name, None),
            type=self.type)
        ast.analyse_semantics(scope_manager, **kwargs)

        # Mark the symbol as initialized.
        symbol = scope_manager.current_scope.get_symbol(self.name)
        symbol.is_mutable = self.tok_mut is not None
        symbol.memory_info.ast_borrowed = self.convention if type(self.convention) is not Asts.ConventionMovAst else None
        symbol.memory_info.is_borrow_mut = isinstance(self.convention, Asts.ConventionMutAst)
        symbol.memory_info.is_borrow_ref = isinstance(self.convention, Asts.ConventionRefAst)
        symbol.memory_info.initialized_by(self)


__all__ = ["FunctionParameterSelfAst"]
