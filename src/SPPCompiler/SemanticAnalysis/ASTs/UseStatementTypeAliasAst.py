from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import copy

from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.Mixins.VisibilityEnabled import AstVisibility
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage3_SupScopeLoader import Stage3_SupScopeLoader
from SPPCompiler.SemanticAnalysis.MultiStage.Stage4_SemanticAnalyser import Stage4_SemanticAnalyser

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.IdentifierAst import IdentifierAst
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager


@dataclass
class UseStatementTypeAliasAst(Ast, Stage2_SymbolGenerator, Stage3_SupScopeLoader, Stage4_SemanticAnalyser):
    new_type: TypeAst
    generic_parameter_group: GenericParameterGroupAst
    tok_assign: TokenAst
    old_type: TypeAst

    _generated: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, TypeAst

        # Convert the name to a TypeAst, and create defaults.
        self.new_type = TypeAst.from_identifier(self.new_type)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.new_type.print(printer),
            self.generic_parameter_group.print(printer),
            self.tok_assign.print(printer),
            self.old_type.print(printer)]
        return "".join(string)

    @staticmethod
    def from_types(new_type: IdentifierAst, generic_parameter_group: Optional[GenericParameterGroupAst], old_type: TypeAst) -> UseStatementTypeAliasAst:
        from SPPCompiler.LexicalAnalysis.TokenType import TokenType
        from SPPCompiler.SemanticAnalysis import TokenAst
        return UseStatementTypeAliasAst(-1, new_type, generic_parameter_group, TokenAst.default(TokenType.TkAssign), old_type)

    def generate_symbols(self, scope_manager: ScopeManager, visibility: AstVisibility = None) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SemanticAnalysis.Scoping.Symbols import TypeSymbol
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Create a class ast for the aliased type, and generate it.
        cls_ast = AstMutation.inject_code(f"cls {self.new_type}", Parser.parse_class_prototype)
        cls_ast.generic_parameter_group = copy.copy(self.generic_parameter_group)
        cls_ast._visibility = visibility
        cls_ast.generate_symbols(scope_manager, alias=True)

        # Create a scope for the alias, allowing its generic arguments to not leak.
        scope_manager.create_and_move_into_new_scope(f"<type-alias:{self.new_type}:{self.pos}>")
        for generic_parameter in self.generic_parameter_group.parameters:
            type_symbol = TypeSymbol(name=generic_parameter.name.types[-1], type=None, is_generic=True)
            scope_manager.current_scope.add_symbol(type_symbol)
        scope_manager.move_out_of_current_scope()

        # Mark this AST as generated, so it is not generated in the analysis phase.
        self._generated = True

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        from SPPCompiler.SemanticAnalysis.Meta.AstMutation import AstMutation
        from SPPCompiler.SyntacticAnalysis.Parser import Parser

        # Skip the scopes that represents the class introduced by this type alias.
        scope_manager.move_to_next_scope()
        while isinstance(scope_manager.current_scope.name, TypeAst):
            scope_manager.move_to_next_scope()

        # Create a sup ast to allow the attribute and method access.
        sup_ast = AstMutation.inject_code(f"sup {self.new_type} ext {self.old_type}", Parser.parse_sup_prototype_inheritance)
        sup_ast.generic_parameter_group = copy.copy(self.generic_parameter_group)
        sup_ast.generate_symbols(scope_manager)

        # Ensure the validity of the old type.
        self.old_type.analyse_semantics(scope_manager)
        old_type_symbol = scope_manager.current_scope.get_symbol(self.old_type)

        # Register the old type against the new alias symbol.
        alias_symbol = scope_manager.current_scope.get_symbol(self.new_type)
        alias_symbol.old_type = old_type_symbol.fq_name
        alias_symbol.old_scope = old_type_symbol.scope

        # Move out of the current scope.
        scope_manager.move_out_of_current_scope()

    def analyse_semantics(self, scope_manager: ScopeManager, **kwargs) -> None:
        # If the symbol has already been generated (module/sup level, skip the scopes).
        if self._generated:
            scope_manager.move_to_next_scope()
            while isinstance(scope_manager.current_scope.name, TypeAst):
                scope_manager.move_to_next_scope()

        # Otherwise, run all the generation and analysis stages, resetting the scope each time.
        else:
            current_scope = scope_manager.current_scope
            self.generate_symbols(scope_manager, **kwargs)

            scope_manager.reset(current_scope)
            self.load_sup_scopes(scope_manager)

            scope_manager.reset(current_scope)
            self.analyse_semantics(scope_manager, **kwargs)


__all__ = ["UseStatementTypeAliasAst"]
