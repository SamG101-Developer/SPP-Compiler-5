from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from SPPCompiler.LexicalAnalysis.TokenType import TokenType
from SPPCompiler.SemanticAnalysis.Meta.Ast import Ast
from SPPCompiler.SemanticAnalysis.Meta.AstPrinter import ast_printer_method, AstPrinter
from SPPCompiler.SemanticAnalysis.MultiStage.Stage1_PreProcessor import Stage1_PreProcessor, PreProcessingContext
from SPPCompiler.SemanticAnalysis.MultiStage.Stage2_SymbolGenerator import Stage2_SymbolGenerator
from SPPCompiler.SemanticAnalysis.MultiStage.Stage3_SupScopeLoader import Stage3_SupScopeLoader
from SPPCompiler.SemanticAnalysis.Scoping.ScopeManager import ScopeManager

if TYPE_CHECKING:
    from SPPCompiler.SemanticAnalysis.ASTs.GenericParameterGroupAst import GenericParameterGroupAst
    from SPPCompiler.SemanticAnalysis.ASTs.SupMemberAst import SupMemberAst
    from SPPCompiler.SemanticAnalysis.ASTs.TokenAst import TokenAst
    from SPPCompiler.SemanticAnalysis.ASTs.TypeAst import TypeAst
    from SPPCompiler.SemanticAnalysis.ASTs.WhereBlockAst import WhereBlockAst
    from SPPCompiler.SemanticAnalysis.ASTs.InnerScopeAst import InnerScopeAst


@dataclass
class SupPrototypeFunctionsAst(Ast, Stage1_PreProcessor, Stage2_SymbolGenerator, Stage3_SupScopeLoader):
    tok_sup: TokenAst
    generic_parameter_group: GenericParameterGroupAst
    name: TypeAst
    where_block: Optional[WhereBlockAst]
    body: InnerScopeAst[SupMemberAst]

    def __post_init__(self) -> None:
        # Import the necessary classes to create default instances.
        from SPPCompiler.SemanticAnalysis import GenericParameterGroupAst, InnerScopeAst
        from SPPCompiler.SemanticAnalysis import WhereBlockAst, TokenAst

        # Create default instances.
        self.tok_sup = self.tok_sup or TokenAst.default(TokenType.KwSup)
        self.generic_parameter_group = self.generic_parameter_group or GenericParameterGroupAst.default()
        self.where_block = self.where_block or WhereBlockAst.default()
        self.body = self.body or InnerScopeAst.default()

    @ast_printer_method
    def print(self, printer: AstPrinter) -> str:
        # Print the AST with auto-formatting.
        string = [
            self.tok_sup.print(printer) + " ",
            self.generic_parameter_group.print(printer),
            self.name.print(printer),
            self.where_block.print(printer),
            self.body.print(printer)]
        return "".join(string)

    def pre_process(self, context: PreProcessingContext) -> None:
        super().pre_process(context)

        # Pre-process the members of this superimposition.
        self.body.members.for_each(lambda m: m.pre_process(self))

    def generate_symbols(self, scope_manager: ScopeManager) -> None:
        ...

    def load_sup_scopes(self, scope_manager: ScopeManager) -> None:
        from SPPCompiler.SemanticAnalysis import ClassPrototypeAst, GlobalConstantAst
        print("Loading sup scopes for superimposition over:", self.name, f"({self.name.without_generics()})")
        print(f"\tCurrent scope: {scope_manager.current_scope}")

        try:
            type_scope = scope_manager.current_scope.get_symbol(self.name.without_generics()).scope
        except AttributeError as e:
            for x in range(100):
                print(next(scope_manager._iterator), end=", ")
            raise e
        print("\tType scope:", type_scope)
        print(f"\tType scope children size {type_scope.children.length}")

        temp_manager = ScopeManager(scope_manager.global_scope, type_scope)
        for member in self.body.members.filter_to_type(GlobalConstantAst):  # , ClassPrototypeAst):
            member.generate_symbols(temp_manager)

        # Todo: I think the class-scopes are being injected into the incorrect place in the "child" list of the parent
        #  scope. There is either no analysis or double analysis, but the shifting of the iterator is not working as
        #  expected.

        # for x in range(self.body.members.filter_to_type(ClassPrototypeAst).length):
        #     print(x)
        #     next(scope_manager._iterator)

        print(f"\tType scope children size {type_scope.children.length}")
        print("\tTemp current scope:", temp_manager.current_scope)
        print("\tCurrent scope:", scope_manager.current_scope)

        # from SPPCompiler.SemanticAnalysis import ClassPrototypeAst, GlobalConstantAst
        # print("Loading sup scopes for superimposition over:", self.name, f"({self.name.without_generics()})")
        #
        # scope_manager._iterator, restore_scope_iterator = itertools.tee(scope_manager._iterator)
        # restore_scope = scope_manager.current_scope
        # print("\tCurrent scope:", restore_scope)
        #
        # type_scope = scope_manager.current_scope.get_symbol(self.name.without_generics()).scope
        # scope_manager.reset(type_scope)
        # print("\tType scope:", type_scope)
        #
        # for member in self.body.members.filter_to_type(GlobalConstantAst):  # ClassPrototypeAst
        #     member.generate_symbols(scope_manager)
        #
        # scope_manager.reset(restore_scope, restore_scope_iterator)
        # print("\tRestored scope:", restore_scope)


__all__ = ["SupPrototypeFunctionsAst"]
