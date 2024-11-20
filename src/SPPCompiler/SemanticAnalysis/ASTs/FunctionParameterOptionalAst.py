from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import functools

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.VariableNameExtraction import VariableNameExtraction
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages
from SPPCompiler.Utils.Sequence import Seq

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.ConventionAst import ConventionAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.LocalVariableAst import LocalVariableAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class FunctionParameterOptionalAst(Ast, Ordered, VariableNameExtraction, CompilerStages):
    variable: LocalVariableAst
    tok_colon: TokenAst
    convention: ConventionAst
    type: TypeAst
    tok_assign: TokenAst
    default: ExpressionAst

    def __post_init__(self) -> None:
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
            self.convention.print(printer),
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    @functools.cached_property
    def extract_names(self) -> Seq[IdentifierAst]:
        return self.variable.extract_names

    @functools.cached_property
    def extract_name(self) -> IdentifierAst:
        return self.variable.extract_name

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import ConventionMovAst, ConventionMutAst, ConventionRefAst, TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the default value.
        if isinstance(self.default, (TokenAst, TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.default)

        # Analyse the type of the default expression.
        self.type.analyse_semantics(scope_manager, **kwargs)
        self.default.analyse_semantics(scope_manager, **kwargs)

        # Check the convention is not a borrow (no way to give a default value as a borrow).
        if not isinstance(self.convention, ConventionMovAst):
            raise SemanticErrors.ParameterOptionalNonBorrowTypeError().add(self.convention)

        # Make sure the default expression is of the correct type.
        default_type = self.default.infer_type(scope_manager)
        target_type = InferredType.from_type(self.type)
        if not target_type.symbolic_eq(default_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self.extract_name, target_type, self.default, default_type)

        # Create the variable for the parameter.
        ast = AstMutation.inject_code(f"let {self.variable}: {self.type}", Parser.parse_let_statement_uninitialized)
        ast.analyse_semantics(scope_manager, **kwargs)

        # Mark the symbol as initialized.
        for name in self.variable.extract_names:
            symbol = scope_manager.current_scope.get_symbol(name)
            symbol.memory_info.ast_borrowed = self.convention if type(self.convention) is not ConventionMovAst else None
            symbol.memory_info.is_borrow_mut = isinstance(self.convention, ConventionMutAst)
            symbol.memory_info.is_borrow_ref = isinstance(self.convention, ConventionRefAst)
            symbol.memory_info.initialized_by(self)


__all__ = ["FunctionParameterOptionalAst"]
