from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.Ordered import Ordered
from SPPCompiler.SemanticAnalysis.Mixins.TypeInferrable import InferredType
from SPPCompiler.SemanticAnalysis.MultiStage.Stages import CompilerStages

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.ExpressionAst import ExpressionAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class GenericCompParameterOptionalAst(Ast, Ordered, CompilerStages):
    tok_cmp: TokenAst
    name: TypeAst
    tok_colon: TokenAst
    type: TypeAst
    tok_assign: TokenAst
    default: ExpressionAst

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import TypeAst

        # Convert the name to a TypeAst.
        self.name = TypeAst.from_identifier(self.name)
        self._variant = "Optional"

    def __eq__(self, other: GenericCompParameterOptionalAst) -> bool:
        # Check both ASTs are the same type and have the same name.
        return isinstance(other, GenericCompParameterOptionalAst) and self.name == other.name

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_cmp.print(printer) + " ",
            self.name.print(printer),
            self.tok_colon.print(printer) + " ",
            self.type.print(printer) + " ",
            self.tok_assign.print(printer) + " ",
            self.default.print(printer)]
        return "".join(string)

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import VariableSymbol
        from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility
        from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst

        # Create a variable symbol for this constant in the current scope (class / function).
        symbol = VariableSymbol(name=IdentifierAst.from_type(self.name), type=self.type, visibility=AstVisibility.Public, is_generic=True)
        symbol.memory_info.ast_pinned.append(self.name)
        symbol.memory_info.ast_comptime_const = self
        symbol.memory_info.initialized_by(self)
        scope_manager.current_scope.add_symbol(symbol)

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        from SPPCompiler.SemanticAnalysis import IdentifierAst, TokenAst, TypeAst
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SemanticAnalysis.Errors.SemanticError import SemanticErrors
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # The ".." TokenAst, or TypeAst, cannot be used as an expression for the default.
        if isinstance(self.default, (TokenAst, TypeAst)):
            raise SemanticErrors.ExpressionTypeInvalidError().add(self.default)

        # Analyse the type of the default expression.
        self.type.analyse_semantics(scope_manager)
        self.default.analyse_semantics(scope_manager)

        # Make sure the default expression is of the correct type.
        default_type = self.default.infer_type(scope_manager)
        target_type = InferredType.from_type(self.type)
        if not target_type.symbolic_eq(default_type, scope_manager.current_scope):
            raise SemanticErrors.TypeMismatchError().add(self.name, target_type, self.default, default_type)

        # Create the variable for the const parameter.
        ast = AstMutation.inject_code(f"let {self.name}: {self.type}", Parser.parse_let_statement_uninitialized)
        ast.analyse_semantics(scope_manager, **kwargs)

        # Mark the symbol as initialized.
        symbol = scope_manager.current_scope.get_symbol(IdentifierAst.from_type(self.name))
        symbol.memory_info.initialized_by(self)


__all__ = ["GenericCompParameterOptionalAst"]
