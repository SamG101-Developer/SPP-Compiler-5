from __future__ import annotations

import functools
from dataclasses import dataclass, field

import std

import SPPCompiler.SemanticAnalysis as Asts
from SPPCompiler.LexicalAnalysis.TokenType import SppTokenType
from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager
from SPPCompiler.SyntacticAnalysis.Parser import SppParser
from SPPCompiler.Utils.Sequence import Seq


@dataclass
class FunctionParameterOptionalAst(Ast, Ordered, VariableNameExtraction):
    variable: Asts.LocalVariableAst = field(default=None)
    tok_colon: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkColon))
    convention: Asts.ConventionAst = field(default_factory=Asts.ConventionMovAst)
    type: Asts.TypeAst = field(default=None)
    tok_assign: Asts.TokenAst = field(default_factory=lambda: Asts.TokenAst.raw(token=SppTokenType.TkAssign))
    default: Asts.ExpressionAst = field(default=None)

    def __post_init__(self) -> None:
        assert self.variable
        assert self.type
        assert self.default
        self._variant = "Optional"

    @std.override_method
    def __eq__(self, other: FunctionParameterOptionalAst) -> bool:
        # Check both ASTs are the same type and have the same variable.
        return isinstance(other, FunctionParameterOptionalAst) and self.variable == other.variable

    @ast_printer_method
    @std.override_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.variable.print(printer),
            self.tok_colon.print(printer) + " ",
            self.convention.print(printer),
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
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
        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the default value.
        if isinstance(self.default, (Asts.TokenAst, Asts.TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.default)

        # Analyse the type of the default expression.
        self.type.analyse_semantics(scope_manager, **kwargs)
        self.default.analyse_semantics(scope_manager, **kwargs)

        # Check the convention is not a borrow (no way to give a default value as a borrow).
        # Todo: remove this check, because of global constants being borrowed?
        # Todo: otherwise, remove from the parser the possibility of a convention for an optional parameter.
        if not isinstance(self.convention, Asts.ConventionMovAst):
            raise SemanticErrors.ParameterOptionalNonBorrowTypeError().add(self.convention)

        # Make sure the default expression is of the correct type.
        default_type = self.default.infer_type(scope_manager)
        target_type = InferredType.from_type(self.type)
        if not target_type.symbolic_eq(default_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self.extract_name, target_type, self.default, default_type)

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


__all__ = ["FunctionParameterOptionalAst"]
