from __future__ import annotations

import functools
from dataclasses import dataclass, field

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class FunctionParameterOptionalAst(Ast, Ordered, VariableNameExtraction):
    variable: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkColon))
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token_type=SppTokenType.TkAssign))
    default: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.variable
        assert self.type
        assert self.default
        self._variant = "Optional"

    def __eq__(self, other: FunctionParameterOptionalAst) -> bool:
        # Check both ASTs are the same type and have the same variable.
        return isinstance(other, FunctionParameterOptionalAst) and self.variable == other.variable

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    @property
    def pos_end(self) -> int:
        return self.default.pos_end

    @functools.cached_property
    def extract_names(self) -> Seq[Asts.IdentifierAst]:
        return self.variable.extract_names

    @functools.cached_property
    def extract_name(self) -> Asts.IdentifierAst:
        return self.variable.extract_name

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the default value.
        if isinstance(self.default, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.default).scopes(scope_manager.current_scope)

        # Analyse the type of the default expression.
        self.type.analyse_semantics(scope_manager, **kwargs)
        self.default.analyse_semantics(scope_manager, **kwargs)

        # Make sure the default expression is of the correct type.
        # Todo: are default_type and self.type the correct way around? test default with a variant.
        default_type = self.default.infer_type(scope_manager)
        if not self.type.symbolic_eq(default_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self.extract_name, self.type, self.default, default_type).scopes(scope_manager.current_scope)

        # Create the variable for the parameter.
        ast = AstMutation.inject_code(
            f"let {self.variable}: {self.type}", SppParser.parse_let_statement_uninitialized,
            pos_adjust=self.variable.pos)
        ast.analyse_semantics(scope_manager, **kwargs)

        # Mark the symbol as initialized.
        convention = self.type.get_convention()
        for name in self.variable.extract_names:
            symbol = scope_manager.current_scope.get_symbol(name)
            symbol.memory_info.ast_borrowed = convention if type(convention) is not Asts.ConventionMovAst else None
            symbol.memory_info.is_borrow_mut = isinstance(convention, Asts.ConventionMutAst)
            symbol.memory_info.is_borrow_ref = isinstance(convention, Asts.ConventionRefAst)
            symbol.memory_info.initialized_by(self)


__all__ = ["FunctionParameterOptionalAst"]
