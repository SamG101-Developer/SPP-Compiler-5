from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import functools, std

from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq
import SPPCompiler.SemanticAnalysis as Asts

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionParameterVariadicAst(Ast, Ordered, VariableNameExtraction, CompilerStages):
    tok_variadic: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkDblDot))
    variable: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkColon))
    convention: Asts.ConventionAst = field(default_factory=Asts.ConventionMovAst)
    type: Asts.TypeAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.variable
        assert self.type
        self._variant = "Variadic"

    @std.override_method
    def __eq__(self, other: FunctionParameterVariadicAst) -> bool:
        # Check both ASTs are the same type and have the same variable.
        return isinstance(other, FunctionParameterVariadicAst) and self.variable == other.variable

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_variadic.print(printer),
            self.variable.print(printer),
            self.tok_colon.print(printer) + " ",
            self.convention.print(printer),
            self.type.print(printer)]
        return "".join(string)

    @functools.cached_property
    @std.override_method
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.variable.extract_names

    @functools.cached_property
    @std.override_method
    def extract_name(self) -> Asts.IdentifierAst:
        return self.variable.extract_name

    @std.override_method
    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # Analyse the type.
        self.type.analyse_semantics(scope_manager, **kwargs)

        # Create the variable for the parameter.
        ast = AstMutation.inject_code(
            f"let {self.variable}: {self.type}",
            SppParser.parse_let_statement_uninitialized)
        ast.analyse_semantics(scope_manager, **kwargs)

        # Mark the symbol as initialized.
        for name in self.variable.extract_names:
            symbol = scope_manager.current_scope.get_symbol(name)
            symbol.memory_info.ast_borrowed = self.convention if type(self.convention) is not Asts.ConventionMovAst else None
            symbol.memory_info.is_borrow_mut = isinstance(self.convention, Asts.ConventionMutAst)
            symbol.memory_info.is_borrow_ref = isinstance(self.convention, Asts.ConventionRefAst)
            symbol.memory_info.initialized_by(self)


__all__ = ["FunctionParameterVariadicAst"]
